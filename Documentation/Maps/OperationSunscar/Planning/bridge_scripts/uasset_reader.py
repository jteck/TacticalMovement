"""
READ-ONLY UE 5.8 .uasset reader.  Opens files 'rb' only; never writes anything.

WHY THIS EXISTS
    When the editor is closed and the MCP bridge on 127.0.0.1:8000 is down, this
    is the only way to read real asset data. Written for the 2026-09-09 ground
    realism audit; recovers material parameters, texture settings, actor classes
    and import graphs straight out of the package binaries.

    Do NOT grep .uasset files for names -- absence of a string in a binary proves
    nothing. Use this instead: a class MUST appear in the import table for an
    object of that class to exist in the package, so absence here IS evidence.

UE 5.8 FORMAT NOTES (hard-won -- read before changing anything)
    * The package summary layout shifted; LegacyFileVersion is -9. Rather than
      parse it, we brute-force locate the name table and then find the
      (nameCount, nameOffset) pair in the header to anchor the rest.
    * Name entries are FString + 2x uint16 hash and are NOT 4-byte aligned.
    * Import entry stride is 40 bytes: ClassPackage(8) ClassName(8)
      OuterIndex(4) ObjectName(8) PackageName(8) bImportOptional(4).
    * Tagged properties use the 5.4+ FPropertyTypeName layout:
          Name FName(8) | TypeName(recursive) | Size int32 | flags uint8 | value
      TypeName = FName(8) + int32 paramCount + paramCount * TypeName.
      There is no separate ArrayIndex field.
    * BoolProperty stores Size = 0 and carries its value in the flags byte:
      bit 0x10 set == true.
    * Do NOT skip 16 bytes for a property GUID when flags == 1; that bit means
      something else in 5.8 and skipping overshoots by 16.
    * ORDER GOTCHA: inside a struct array element, a derived struct's own
      properties serialize BEFORE the base struct's. So for a static switch,
      'Value' appears ~74 bytes BEFORE its ParameterInfo 'Name'. Scalars are the
      other way round. params() handles scalars/textures; read bools separately.

USAGE
    from uasset_reader import Pkg, Props
    p  = Pkg('Content/.../MI_Something.uasset')
    pr = Props(p)
    for e in p.imports(): print(e['cls'], e['name'])
    for off, name, ty, val in pr.params(): print(name, ty, val)
"""
import struct


class Pkg:
    def __init__(s, path):
        s.path = path
        with open(path, 'rb') as f:
            s.d = f.read()
        if struct.unpack_from('<I', s.d, 0)[0] != 0x9E2A83C1:
            raise ValueError("not a uasset: %s" % path)
        s.nameOffset, s.names = s._findnames()
        s.nameCount = len(s.names)
        s._summary()

    # ---- name table -------------------------------------------------------
    def _try(s, o, maxn=40000):
        d, out, p = s.d, [], o
        while len(out) < maxn and p + 4 <= len(d):
            n = struct.unpack_from('<i', d, p)[0]
            p += 4
            if n <= 0 or n > 400:
                break
            b = d[p:p + n]
            p += n
            if len(b) < n or b[-1] != 0:
                break
            try:
                nm = b[:-1].decode('ascii')
            except UnicodeDecodeError:
                break
            if any(ord(c) < 32 or ord(c) > 126 for c in nm):
                break
            out.append(nm)
            p += 4                      # two uint16 hashes
        return out

    def _findnames(s):
        best = (0, [])
        for o in range(0, min(len(s.d), 9000)):
            r = s._try(o)
            if len(r) > len(best[1]):
                best = (o, r)
        return best

    def _summary(s):
        d = s.d
        s.importCount = s.importOffset = s.exportCount = s.exportOffset = None
        i = d.find(struct.pack('<ii', s.nameCount, s.nameOffset))
        if i < 0:
            return
        o = i + 8
        o += 8                                        # SoftObjectPaths count/offset
        n = struct.unpack_from('<i', d, o)[0]
        o += 4 + max(n, 0)                            # LocalizationId FString
        o += 8                                        # GatherableTextData
        s.exportCount = struct.unpack_from('<i', d, o)[0]
        s.exportOffset = struct.unpack_from('<i', d, o + 4)[0]
        s.importCount = struct.unpack_from('<i', d, o + 8)[0]
        s.importOffset = struct.unpack_from('<i', d, o + 12)[0]

    def n(s, i):
        return s.names[i] if 0 <= i < len(s.names) else '?%d' % i

    def imports(s):
        if not s.importOffset or not s.importCount:
            return []
        stride = (s.exportOffset - s.importOffset) // s.importCount
        out = []
        for k in range(s.importCount):
            o = s.importOffset + k * stride
            g = lambda x: struct.unpack_from('<i', s.d, o + x)[0]
            out.append(dict(classPkg=s.n(g(0)), cls=s.n(g(8)), outer=g(16),
                            name=s.n(g(20)),
                            pkg=s.n(g(28)) if stride >= 36 else ''))
        return out

    def objref(s, idx):
        """FPackageIndex -> readable name (negative == import)."""
        if idx < 0:
            imp = s.imports()
            k = -idx - 1
            if 0 <= k < len(imp):
                e = imp[k]
                full = e['name']
                if e['outer'] < 0:
                    j = -e['outer'] - 1
                    if 0 <= j < len(imp):
                        full = imp[j]['name'] + '.' + e['name']
                return full + ' [%s]' % e['cls']
        return 'export#%d' % idx if idx > 0 else 'None'


class Props:
    """Pattern-based tagged-property reader (UE 5.4+ FPropertyTypeName layout)."""

    def __init__(s, pkg):
        s.p, s.d, s.N = pkg, pkg.d, pkg.names

    def nm(s, i):
        return s.N[i] if 0 <= i < len(s.N) else '?%d' % i

    def fname(s, o):
        return s.nm(struct.unpack_from('<i', s.d, o)[0]), o + 8

    def typename(s, o, depth=0):
        if depth > 6:
            raise ValueError('type nesting too deep')
        n, o = s.fname(o)
        c = struct.unpack_from('<i', s.d, o)[0]
        o += 4
        if not (0 <= c <= 8):
            raise ValueError('bad type param count')
        ps = []
        for _ in range(c):
            t, o = s.typename(o, depth + 1)
            ps.append(t)
        return (n, ps), o

    def tag(s, o):
        """-> (name, type, size, valueOffset, flagsByte)."""
        name, o2 = s.fname(o)
        if name == 'None':
            return name, None, 0, o2, 0
        ty, o2 = s.typename(o2)
        size = struct.unpack_from('<i', s.d, o2)[0]
        o2 += 4
        f = s.d[o2]
        o2 += 1
        return name, ty, size, o2, f

    def scan(s, propname):
        """Every byte offset whose FName == propname and that parses as a tag."""
        try:
            idx = s.N.index(propname)
        except ValueError:
            return []
        pat = struct.pack('<ii', idx, 0)
        out, i = [], 0
        while True:
            i = s.d.find(pat, i)
            if i < 0:
                break
            try:
                n, ty, size, vo, f = s.tag(i)
                if n == propname and ty and 0 <= size < len(s.d):
                    out.append((i, ty, size, vo, f))
            except Exception:
                pass
            i += 1
        return out

    def value(s, ty, vo, size, flags):
        t = ty[0]
        if t == 'FloatProperty':
            return struct.unpack_from('<f', s.d, vo)[0]
        if t == 'DoubleProperty':
            return struct.unpack_from('<d', s.d, vo)[0]
        if t in ('IntProperty', 'Int32Property'):
            return struct.unpack_from('<i', s.d, vo)[0]
        if t == 'UInt32Property':
            return struct.unpack_from('<I', s.d, vo)[0]
        if t == 'BoolProperty':
            return bool(flags & 0x10)              # value lives in the flags byte
        if t in ('NameProperty', 'EnumProperty'):
            return s.fname(vo)[0]
        if t == 'ByteProperty':
            return s.fname(vo)[0] if size >= 8 else s.d[vo]
        if t == 'ObjectProperty':
            return s.p.objref(struct.unpack_from('<i', s.d, vo)[0])
        if t == 'StrProperty':
            n = struct.unpack_from('<i', s.d, vo)[0]
            return s.d[vo + 4:vo + 4 + n].decode('utf-8', 'replace').rstrip('\x00')
        if t == 'ArrayProperty':
            return 'array[%d]' % struct.unpack_from('<i', s.d, vo)[0]
        if t == 'StructProperty':
            sub = ty[1][0][0] if ty[1] else ''
            if sub == 'LinearColor':
                return tuple(round(x, 4) for x in struct.unpack_from('<4f', s.d, vo))
            if sub == 'Vector':
                return tuple(round(x, 3) for x in struct.unpack_from('<3d', s.d, vo))
            if sub == 'Vector2D':
                return tuple(round(x, 3) for x in struct.unpack_from('<2d', s.d, vo))
            if sub == 'IntPoint':
                return tuple(struct.unpack_from('<2i', s.d, vo))
            if sub == 'Guid':
                return s.d[vo:vo + 16].hex()
            return '<%s %dB>' % (sub, size)
        return '<%s %dB>' % (t, size)

    def get(s, propname):
        """First occurrence of a top-level property, decoded. None if absent."""
        h = s.scan(propname)
        if not h:
            return None
        o, ty, size, vo, f = h[0]
        return s.value(ty, vo, size, f)

    def params(s):
        """Material-instance parameters: pair each ParameterValue with the
        nearest PRECEDING ParameterInfo 'Name'. Correct for scalar / vector /
        texture parameters. NOT correct for static switches -- see switches()."""
        names = sorted((o, s.fname(vo)[0])
                       for o, ty, sz, vo, f in s.scan('Name')
                       if ty[0] == 'NameProperty')
        out = []
        for off, ty, size, vo, f in s.scan('ParameterValue'):
            pn = None
            for o2, v in names:
                if o2 < off:
                    pn = v
                else:
                    break
            out.append((off, pn, ty[0], s.value(ty, vo, size, f)))
        out.sort()
        return out

    def switches(s):
        """Static switch parameters. The bool 'Value' serializes BEFORE its
        ParameterInfo 'Name', so pair each with the NEXT name."""
        names = sorted((o, s.fname(vo)[0])
                       for o, ty, sz, vo, f in s.scan('Name')
                       if ty[0] == 'NameProperty')
        out = []
        for off, ty, size, vo, f in sorted(s.scan('Value')):
            if ty[0] != 'BoolProperty':
                continue
            nxt = [v for o2, v in names if o2 > off]
            out.append((nxt[0] if nxt else '?', bool(f & 0x10)))
        return out


if __name__ == '__main__':
    import sys
    for path in sys.argv[1:]:
        p = Pkg(path)
        pr = Props(p)
        print('=== %s ===' % path)
        print('  names %d  imports %s  exports %s'
              % (p.nameCount, p.importCount, p.exportCount))
        for off, name, ty, val in pr.params():
            print('  %-34s %-16s %s' % (name, ty, val))
        for name, val in pr.switches():
            print('  %-34s %-16s %s' % (name, 'StaticSwitch', val))
