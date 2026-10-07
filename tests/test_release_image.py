import unittest, subprocess, tempfile, pathlib, struct, sys, json, base64, importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ImageValidation(unittest.TestCase):
 def test_new_release_channel_versions(self):
  spec=importlib.util.spec_from_file_location('sign_manifest',ROOT/'tools/sign_manifest.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  for channel,version in [('pilot','0.4.7-pilot.1'),('pilot','0.4.7-pilot.10'),('stable','0.4.7')]:
   module.require_channel_version(channel,version)
  for channel,version in [('pilot','0.4.7'),('pilot','0.4.7-pilot.0'),('pilot','0.4.7-pilot.01'),('stable','0.4.7-pilot.1')]:
   with self.assertRaises(SystemExit):module.require_channel_version(channel,version)
 def test_wrong_version_rejected_before_signing(self):
  with tempfile.TemporaryDirectory() as folder:
   p=pathlib.Path(folder); image=bytearray(65536); image[0]=0xE9;struct.pack_into('<H',image,12,9);struct.pack_into('<I',image,32,0xABCD5432);image[48:54]=b'0.4.2\0';image[300:320]=b'esp32s3wood-n16r8\0'.ljust(20,b'\0');(p/'image.bin').write_bytes(image);(p/'key.pem').write_text('placeholder')
   result=subprocess.run([sys.executable,'tools/sign_manifest.py','--image',str(p/'image.bin'),'--private-key',str(p/'key.pem'),'--version','0.4.3','--generation','2','--security-version','0','--board','esp32s3wood-n16r8','--partition-layout','ota-v1-4m','--asset-name','image.bin','--min-updater','0.4.1','--notes-de','Test','--notes-en','Test','--output',str(p/'manifest.json')],cwd=ROOT,capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('differs from application version',result.stderr)

 def test_echo_n16_requires_four_megabyte_layout(self):
  payload=dict(product='rp-phone',channel='pilot',generation=1,version='0.4.4',security_version=0,board='esp32s3echobase-n16r8',chip='esp32s3',partition_layout='ota-v1-4m',size=1454944,sha256='a'*64,url='https://github.com/chkronenberg/rp-firmware-update/releases/download/v0.4.4/image.bin',min_updater='0.4.3',notes_de='Test',notes_en='Test')
  with tempfile.TemporaryDirectory() as folder:
   target=pathlib.Path(folder)/'manifest.json'
   for layout,valid in [('ota-v1-4m',True),('ota-v1-2m',False)]:
    payload['partition_layout']=layout
    target.write_text(json.dumps(dict(schema=1,algorithm='ECDSA-P256-SHA256',key_id='prod-2026-01',payload=base64.b64encode(json.dumps(payload).encode()).decode(),signature=base64.b64encode(b'structure-test-only').decode())))
    result=subprocess.run([sys.executable,'tools/validate_manifest.py',str(target)],cwd=ROOT,capture_output=True,text=True)
    self.assertEqual(result.returncode==0,valid,result.stderr)
