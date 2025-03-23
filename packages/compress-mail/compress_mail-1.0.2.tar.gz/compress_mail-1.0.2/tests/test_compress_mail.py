import pytest
from unittest.mock import patch, MagicMock
import signal
from compress_mail.compress_mail import MaildirLock, MailCompressor

# @patch('subprocess.run')
# def test_lock_success(mock_run):
#     mock_run.return_value = MagicMock(returncode=0, stdout='1234')
#     lock = MaildirLock('/path/to/control', 10)
#     with lock:
#         assert lock.pid == '1234'


@patch('subprocess.run')
def test_lock_failure(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stderr='Error')
    lock = MaildirLock('/path/to/control', 10)
    with pytest.raises(Exception):
        with lock:
            pass


@patch('os.kill')
@patch('subprocess.run')
def test_unlock(mock_run, mock_kill):
    mock_run.return_value = MagicMock(returncode=0, stdout='1234')
    lock = MaildirLock('/path/to/control', 10)
    with lock:
        pass
    mock_kill.assert_called_once_with(1234, signal.SIGTERM)


@patch('os.walk')
def test_find_mails_to_compress(mock_walk):
    mock_walk.return_value = [
        (
            '/path/to/maildir',
            [],
            ['1742423129.M60927P26663.fully,S=30457,W=30918:2,S', '1742423130.M622371P26663.fully,S=12796,W=12984:2,S'],
        )
    ]
    compressor = MailCompressor('/path/to/maildir', '/tmp', '/control', 10, 'gzip', False)
    mails = compressor.find_mails_to_compress()
    assert len(mails) == 2


@patch('shutil.copy2')
@patch('subprocess.run')
def test_compress_mails_gzip(mock_run, mock_copy):
    compressor = MailCompressor('/path/to/maildir', '/tmp', '/control', 10, 'gzip', False)
    mails = ['/path/to/maildir/mail1:2,']
    compressed_files = compressor.compress_mails(mails)
    assert len(compressed_files) == 1
    mock_run.assert_called_with(['gzip', '-6', '/tmp/mail1:2,'])


@patch('os.utime')
@patch('os.path.getmtime')
def test_update_mtime(mock_getmtime, mock_utime):
    mock_getmtime.return_value = 1234567890
    compressor = MailCompressor('/path/to/maildir', '/tmp', '/control', 10, 'gzip', False)
    original_files = ['/path/to/maildir/mail1:2,']
    compressed_files = ['/tmp/mail1:2,.gz']
    compressor.update_mtime(original_files, compressed_files)
    mock_utime.assert_called_with('/tmp/mail1:2,.gz', (1234567890, 1234567890))


@patch('os.rename')
@patch('os.remove')
@patch('os.path.exists')
def test_verify_and_replace_mails(mock_exists, mock_remove, mock_rename):
    mock_exists.return_value = True
    compressor = MailCompressor('/path/to/maildir', '/tmp', '/control', 10, 'gzip', False)
    original_files = ['/path/to/maildir/mail1:2,']
    compressed_files = ['/tmp/mail1:2,.gz']
    compressor.verify_and_replace_mails(original_files, compressed_files)
    mock_rename.assert_any_call('/tmp/mail1:2,.gz', '/path/to/maildir/mail1:2,')
    mock_rename.assert_any_call('/path/to/maildir/mail1:2,', '/path/to/maildir/mail1:2,SZ')


@patch('compress_mail.compress_mail.MaildirLock')
def test_run_with_lock(mock_lock):
    compressor = MailCompressor('/path/to/maildir', '/tmp', '/control', 10, 'gzip', True)
    compressor.find_mails_to_compress = MagicMock(return_value=['/path/to/maildir/mail1:2,'])
    compressor.compress_mails = MagicMock(return_value=['/tmp/mail1:2,.gz'])
    compressor.update_mtime = MagicMock()
    compressor.verify_and_replace_mails = MagicMock()
    compressor.run()
    mock_lock.assert_called_once_with('/control', 10)
    compressor.verify_and_replace_mails.assert_called_once()


def test_run_without_lock():
    compressor = MailCompressor('/path/to/maildir', '/tmp', '/control', 10, 'gzip', False)
    compressor.find_mails_to_compress = MagicMock(return_value=['/path/to/maildir/mail1:2,'])
    compressor.compress_mails = MagicMock(return_value=['/tmp/mail1:2,.gz'])
    compressor.update_mtime = MagicMock()
    compressor.verify_and_replace_mails = MagicMock()
    compressor.run()
    compressor.verify_and_replace_mails.assert_called_once()
