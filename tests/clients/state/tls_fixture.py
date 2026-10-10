"""Prepare task-owned short-lived TLS input; never installs host/device trust."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
import argparse,hashlib,ipaddress,json,os
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID,ExtendedKeyUsageOID
p=argparse.ArgumentParser();p.add_argument("--prepare",action="store_true",required=True);a=p.parse_args()
root=Path("H:/IM-platform/.git/worktrees/IM-platform43/state-runtime/tls-state-week2").resolve()
if root.exists():raise RuntimeError("Never replace prior TLS input")
root.mkdir(parents=True)
now=datetime.now(timezone.utc);end=now+timedelta(days=7)
key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,"IM STATE owned fixture 20261010")])
ca=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=5)).not_valid_after(end).add_extension(x509.BasicConstraints(ca=True,path_length=0),True).add_extension(x509.KeyUsage(False,False,False,False,False,True,True,False,False),True).add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()),False).add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()),False).add_extension(x509.NameConstraints([x509.DNSName("localhost"),x509.IPAddress(ipaddress.ip_network("127.0.0.1/32"))],None),True).sign(key,hashes.SHA256()))
serverkey=rsa.generate_private_key(public_exponent=65537,key_size=2048)
server=(x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,"localhost")])).issuer_name(name).public_key(serverkey.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=5)).not_valid_after(end).add_extension(x509.BasicConstraints(ca=False,path_length=None),True).add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost"),x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]),False).add_extension(x509.SubjectKeyIdentifier.from_public_key(serverkey.public_key()),False).add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()),False).add_extension(x509.KeyUsage(True,False,True,False,False,False,False,False,False),True).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),False).sign(key,hashes.SHA256()))
for label,cert in [("ca",ca),("server",server)]:
 (root/(label+".pem")).write_bytes(cert.public_bytes(serialization.Encoding.PEM))
 (root/(label+".der")).write_bytes(cert.public_bytes(serialization.Encoding.DER))
(root/"server.key").write_bytes(serverkey.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
public={"task_id":"LOOP1-CLIENT-STATE-001","directory":str(root),"hosts":["localhost","127.0.0.1"],"endpoint":"https://localhost:18443","notAfterUTC":end.isoformat(),"caSHA256":ca.fingerprint(hashes.SHA256()).hex(),"caWindowsThumbprintSHA1":ca.fingerprint(hashes.SHA1()).hex(),"caPEMSHA256":hashlib.sha256((root/"ca.pem").read_bytes()).hexdigest(),"serverSHA256":server.fingerprint(hashes.SHA256()).hex(),"trust_installed":False,"ca_private_key_saved":False}
(root/"public.json").write_text(json.dumps(public,indent=2)+"\n",encoding="utf-8")
Path("spec/progress/evidence/LOOP1-CLIENT-STATE-001/tls-prepared.json").write_text(json.dumps(public,indent=2)+"\n",encoding="utf-8")
print(json.dumps(public,indent=2))
