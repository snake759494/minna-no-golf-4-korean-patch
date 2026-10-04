"""이 원본의 ISO9660/UDF 브리지 및 게임 내 LBA 목록 갱신."""
import struct,binascii
SECTOR=2048
_udf_positions=None
def both(n):return struct.pack('<I',n)+struct.pack('>I',n)
def tag(b):
    size=struct.unpack_from('<H',b,10)[0]
    struct.pack_into('<H',b,8,binascii.crc_hqx(b[16:16+size],0))
    b[4]=sum(v for i,v in enumerate(b[:16]) if i!=4)&255
def relocate(f,record,new_lba,new_size,inventory):
    global _udf_positions
    parent=record['path'].rsplit('/',1)[0];name=record['path'].rsplit('/',1)[1].encode('ascii')
    directory=next(r for r in inventory if r['path']==parent)
    pos=directory['lba']*SECTOR;f.seek(pos);b=bytearray(f.read(directory['size']));p=0;found=0
    while p<len(b):
        n=b[p]
        if not n:p=(p//SECTOR+1)*SECTOR;continue
        if b[p+33:p+33+b[p+32]]==name:
            assert struct.unpack_from('<I',b,p+2)[0]==record['lba']
            b[p+2:p+10]=both(new_lba);b[p+10:p+18]=both(new_size);found+=1
        p+=n
    assert found==1;f.seek(pos);f.write(b)
    if _udf_positions is None:
        _udf_positions={}
        for sector in range(547,7321):
            f.seek(sector*SECTOR);entry=f.read(SECTOR)
            if struct.unpack_from('<H',entry)[0]!=261:continue
            lea,lad=struct.unpack_from('<II',entry,168)
            if lad!=8 or lea>1800:continue
            size,lba=struct.unpack_from('<II',entry,176+lea)
            _udf_positions.setdefault((lba+547,size),[]).append(sector)
    found=0
    for sector in _udf_positions.get((record['lba'],record['size']),[]):
        f.seek(sector*SECTOR);b=bytearray(f.read(SECTOR))
        if struct.unpack_from('<H',b)[0]!=261:continue
        lea,lad=struct.unpack_from('<II',b,168)
        if lad!=8 or lea>1800:continue
        size,lba=struct.unpack_from('<II',b,176+lea)
        if lba+547!=record['lba'] or size!=record['size']:continue
        struct.pack_into('<II',b,176+lea,new_size,new_lba-547)
        struct.pack_into('<Q',b,56,new_size);struct.pack_into('<Q',b,64,(new_size+2047)//2048)
        tag(b);f.seek(sector*SECTOR);f.write(b);found+=1
    assert found==1,('UDF 파일 엔트리',record['path'],found)
def resize(f,old_sectors,new_sectors):
    f.seek(16*SECTOR);b=bytearray(f.read(SECTOR));b[80:88]=both(new_sectors);f.seek(16*SECTOR);f.write(b)
    for lba in [34,50]:
        f.seek(lba*SECTOR);b=bytearray(f.read(SECTOR));assert struct.unpack_from('<H',b)[0]==5
        struct.pack_into('<I',b,192,new_sectors-1-547);tag(b);f.seek(lba*SECTOR);f.write(b)
    f.seek(64*SECTOR);b=bytearray(f.read(SECTOR));assert struct.unpack_from('<HI',b)[0]==9
    struct.pack_into('<I',b,84,new_sectors-1-547);tag(b);f.seek(64*SECTOR);f.write(b)
    f.seek((old_sectors-1)*SECTOR);b=bytearray(f.read(SECTOR));assert struct.unpack_from('<H',b)[0]==2
    struct.pack_into('<I',b,12,new_sectors-1);tag(b);f.seek((new_sectors-1)*SECTOR);f.write(b)
