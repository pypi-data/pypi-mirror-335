import subprocess
import io
from dotenv import dotenv_values

class OpenSSL:
    @staticmethod
    def load_encrypted_dotenvsecret(file_path, password, iteration=100):
        """
        Dekripsi file terenkripsi langsung ke memori dan gunakan dotenv untuk memuatnya.
        
        :param file_path: Path ke file terenkripsi (.env.enc atau .envsecret)
        :param password: Password untuk mendekripsi file
        :param iteration: Jumlah iterasi untuk PBKDF2 (default: 100)
        :return: Dictionary dari key-value hasil parsing dotenv
        """
        try:
            # Dekripsi file menggunakan OpenSSL dengan iterasi yang dapat diatur
            result = subprocess.run(
                [
                    "openssl", "enc", "-aes-256-cbc", "-d", "-pbkdf2",
                    "-iter", str(iteration), "-in", file_path, "-k", password
                ],
                capture_output=True,
                text=True,  # Menangkap output sebagai string
                check=True
            )
            decrypted_content = result.stdout  # Isi file hasil dekripsi

            # Memuat hasil dekripsi ke dalam dotenv
            return dotenv_values(stream=io.StringIO(decrypted_content))  # Parsing ke dictionary
        except subprocess.CalledProcessError as e:
            error_message = e.stderr if e.stderr else "Unknown error"
            print(f"[ERROR] Gagal mendekripsi file: {error_message}")
            return None  # Bisa juga raise exception jika ingin debugging lebih ketat
