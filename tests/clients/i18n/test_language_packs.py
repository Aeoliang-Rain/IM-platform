import importlib.util
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('language_pack_build',ROOT/'tools/build_language_packs.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class LanguagePackBuild(unittest.TestCase):
 def test_real_sources_reproduce_independent_json_artifacts(self):
  first=builder.verify(ROOT);self.assertEqual(first,builder.verify(ROOT))
  self.assertEqual(set(first),{'en.json','ja-JP.json','manifest.json'})
  self.assertEqual(builder.parse_json(first['manifest.json'])['publication'],'NOT_PUBLISHED')
  data=builder.sources(ROOT)
  for locale in ('en','ja-JP'):self.assertEqual(builder.parse_json(first[locale+'.json'])['messages'],data[locale])
 def test_negative_keys_parameters_types_and_duplicates(self):
  for data in ({'en':{'k':'{name}'},'zh-CN':{'k':'{name}'},'ja-JP':{'k':'{other}'}},{'en':{'k':'v'},'zh-CN':{},'ja-JP':{'k':'v'}},{'en':{'k':1},'zh-CN':{'k':1},'ja-JP':{'k':1}}):
   with self.subTest(data=data):
    with self.assertRaises((ValueError,TypeError)):builder.artifacts(data)
  for raw in ('{"x":"a","x":"b"}','{"__proto__":"a"}'):
   with self.assertRaises(ValueError):builder.parse_json(raw)
 def test_unknown_output_is_preserved(self):
  with tempfile.TemporaryDirectory() as temporary:
   directory=Path(temporary);unknown=directory/'unknown.txt';unknown.write_text('preserve')
   with self.assertRaises(ValueError):builder.write_owned(directory,{'manifest.json':b'{}'})
   self.assertEqual(unknown.read_text(),'preserve')
if __name__=='__main__':unittest.main()
