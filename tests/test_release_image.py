import unittest, subprocess, tempfile, pathlib, struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ImageValidation(unittest.TestCase):
 def test_wrong_version_rejected_before_signing(self):
  with tempfile.TemporaryDirectory() as folder:
   p=pathlib.Path(folder); image=bytearray(65536); image[0]=0xE9;struct.pack_into('<H',image,12,9);struct.pack_into('<I',image,32,0xABCD5432);image[48:54]=b'0.4.2\0';image[300:320]=b'esp32s3wood-n16r8\0'.ljust(20,b'\0');(p/'image.bin').write_bytes(image);(p/'key.pem').write_text('placeholder')
   result=subprocess.run(['python','tools/sign_manifest.py','--image',str(p/'image.bin'),'--private-key',str(p/'key.pem'),'--version','0.4.3','--generation','2','--security-version','0','--board','esp32s3wood-n16r8','--partition-layout','ota-v1-4m','--asset-name','image.bin','--min-updater','0.4.1','--notes-de','Test','--notes-en','Test','--output',str(p/'manifest.json')],cwd=ROOT,capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('differs from application version',result.stderr)
