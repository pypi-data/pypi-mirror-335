import os
import shutil
import subprocess
import re
import logging
import signal

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import track

from compress_mail._version import __version__

console = Console()


def sizeof_fmt(num, suffix='B', units=None, power=None, sep='', precision=2, sign=False):
    sign = '+' if sign and num > 0 else ''
    fmt = '{0:{1}.{2}f}{3}{4}{5}'
    prec = 0
    for unit in units[:-1]:
        if abs(round(num, precision)) < power:
            break
        num /= float(power)
        prec = precision
    else:
        unit = units[-1]
    return fmt.format(num, sign, prec, sep, unit, suffix)


def sizeof_fmt_iec(num, suffix='B', sep='', precision=2, sign=False):
    return sizeof_fmt(
        num,
        suffix=suffix,
        sep=sep,
        precision=precision,
        sign=sign,
        units=['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'],
        power=1024,
    )


def sizeof_fmt_decimal(num, suffix='B', sep='', precision=2, sign=False):
    return sizeof_fmt(
        num,
        suffix=suffix,
        sep=sep,
        precision=precision,
        sign=sign,
        units=['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'],
        power=1000,
    )


class MaildirLock:
    def __init__(self, control_dir, timeout=10):
        self.timeout = timeout
        self.control_dir = control_dir
        self.pid = None

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unlock()

    def lock(self):
        result = subprocess.run(['maildirlock', self.control_dir, str(self.timeout)], capture_output=True, text=True)
        if result.returncode == 0:
            self.pid = result.stdout.strip()
            logging.info(f'Successfully locked maildir at path {self.control_dir}')
        else:
            logging.error(f'Failed to lock maildir: {result.stderr}')
            raise Exception(f'Failed to lock maildir: {result.stderr}')

    def unlock(self):
        if self.pid:
            os.kill(int(self.pid), signal.SIGTERM)
            logging.info(f'Unlocked maildir with PID {self.pid}')


class MailCompressor:
    def __init__(self, maildir, tmp_dir, control_dir, timeout, compression_method, use_lock):
        self.maildir = maildir
        self.tmp_dir = tmp_dir
        self.control_dir = control_dir
        self.timeout = timeout
        self.compression_method = compression_method
        self.use_lock = use_lock
        self.pid = None
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO, format='%(message)s', datefmt='[%X]', handlers=[RichHandler(show_path=False)]
        )

    def check_binaries(self):
        required_binaries = [self.compression_method]
        if self.use_lock:
            required_binaries.append('maildirlock')
        for binary in required_binaries:
            if not shutil.which(binary):
                raise FileNotFoundError(f'Required binary not found: {binary}')
        logging.info('All required binaries are present')

    def find_mails_to_compress(self):
        mails_to_compress = []
        for root, dirs, files in os.walk(self.maildir):
            for filename in track(files, description='Searching for mails'):
                if re.search(r'S=\d+', filename) and 'Z' not in filename.split(':')[1]:
                    mails_to_compress.append(os.path.join(root, filename))
        if mails_to_compress:
            logging.info(f'Found {len(mails_to_compress)} mails to compress')
        else:
            logging.info('No mails found to compress')
        return mails_to_compress

    def compress_mails(self, mails):
        compressed_files = []
        for mail in track(mails, description='Compressing mails'):
            compressed_file = os.path.join(self.tmp_dir, os.path.basename(mail))
            shutil.copy2(mail, compressed_file)
            if self.compression_method == 'gzip':
                subprocess.run(['gzip', '-6', compressed_file])
                compressed_files.append(compressed_file + '.gz')
            elif self.compression_method == 'zstd':
                subprocess.run(['zstd', '-3', '--rm', '-q', '-T0', compressed_file])
                compressed_files.append(compressed_file + '.zst')
        logging.info(f'Compressed {len(compressed_files)} mails using {self.compression_method}')
        return compressed_files

    def update_mtime(self, original_files, compressed_files):
        zipped = list(zip(original_files, compressed_files))
        for original, compressed in track(zipped, description='Updating mtime'):
            original_mtime = os.path.getmtime(original)
            os.utime(compressed, (original_mtime, original_mtime))
        logging.info('Updated mtimes for compressed files')

    def verify_and_replace_mails(self, original_files, compressed_files):
        zipped = list(zip(original_files, compressed_files))
        for original, compressed in track(zipped, description='Verifying/replacing mails'):
            if os.path.exists(original):
                os.rename(compressed, original)
                new_filename = re.sub(r'(:2,)(.*)', r'\1SZ', original)
                os.rename(original, new_filename)
            else:
                os.remove(compressed)
        logging.info('Verified and replaced original mails with compressed ones')

    def get_directory_size(self, directory):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def run(self):
        try:
            logging.info('Starting maildir compression process')
            self.check_binaries()
            initial_size = self.get_directory_size(self.maildir)
            logging.info(f'Initial maildir size: {sizeof_fmt_decimal(initial_size)}')

            mails_to_compress = self.find_mails_to_compress()
            if not mails_to_compress:
                return

            compressed_files = self.compress_mails(mails_to_compress)
            self.update_mtime(mails_to_compress, compressed_files)

            if self.use_lock:
                with MaildirLock(self.control_dir, self.timeout):
                    self.verify_and_replace_mails(mails_to_compress, compressed_files)
            else:
                self.verify_and_replace_mails(mails_to_compress, compressed_files)

            final_size = self.get_directory_size(self.maildir)
            logging.info(f'Final maildir size: {sizeof_fmt_decimal(final_size)}')

            savings = ((initial_size - final_size) / initial_size) * 100
            logging.info(f'Disk savings: {savings:.2f}%')

            logging.info('Completed maildir compression process')

        except FileNotFoundError as e:
            logging.error(f'Error occurred: {e}')


@click.command()
@click.option('--maildir', '-m', required=True, help='Path to the Maildir')
@click.option('--tmp-dir', '-t', required=True, help='Path to the temporary directory for compression')
@click.option('--control-dir', '-c', required=True, help='Path to the control directory containing dovecot-uidlist')
@click.option('--timeout', type=int, default=10, help='Timeout for maildirlock')
@click.option(
    '--compression',
    '-z',
    type=click.Choice(['gzip', 'zstd']),
    default='gzip',
    help='Compression method to use (gzip or zstd)',
)
@click.option('--lock/--no-lock', '-l', is_flag=True, default=True, help='Use maildir locking mechanism')
@click.version_option(version=__version__)
def main(maildir, tmp_dir, control_dir, timeout, compression, lock):
    compressor = MailCompressor(
        maildir=maildir,
        tmp_dir=tmp_dir,
        control_dir=control_dir,
        timeout=timeout,
        compression_method=compression,
        use_lock=lock,
    )
    compressor.run()


if __name__ == '__main__':
    main()
