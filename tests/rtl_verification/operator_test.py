from testcase import *

def twos(x):
	if x < 0:
		return ((-x ^ 0xffffffff) + 1) & 0xffffffff
	else:
		return x

class OperatorTests(TestCase):
	def test_vectorIntegerCompare():	
		BU = 0xc0800018		# Big unsigned
		BS = 0x60123498		# Big signed
		SM = 1	# Small
	
		return ({ 	'v0' : [ BU, BS, BU, BS, BU, SM, BS, SM, BU, BS, BU, BS, BU, SM, BS, SM ],
					'v1' : [ BU, BS, BS, BU, SM, BU, SM, BS, BU, BS, BS, BU, SM, BU, SM, BS ] },
			'''
				s0 = 15
				cr30 = s0	; Enable all threads
				
				s0 = vi0 == vi1
				s1 = vi0 <> vi1
				s2 = vi0 > vi1  
				s3 = vi0 < vi1
				s4 = vi0 >= vi1
				s5 = vi0 <= vi1
				s6 = vu0 > vu1
				s7 = vu0 < vu1
				s8 = vu0 >= vu1
				s9 = vu0 <= vu1
			''',
			{ 	'u0' : 0xc0c0,
				'u1' : 0x3f3f,
				'u2' : 0x1616,   # 00010110
				'u3' : 0x2929,	 # 00101001
				'u4' : 0xd6d6,	 # 11010110
				'u5' : 0xe9e9,	 # 11101001
				'u6' : 0x2626,	 # 00100110
				'u7' : 0x1919,	 # 00011001
				'u8' : 0xe6e6,   # 11100110
				'u9' : 0xd9d9 	 # 11011001
			}, None, None, None) 
		
	def test_registerOps():
		OP1 = 0x19289adf
		OP2 = 0x2374bdad
			 
		return ({ 'u0' : OP1, 'u1' : OP2, 'u20' : 5},
			'''
				u2 = 15
				cr30 = u2	; Enable all threads

				u2 = u0 | u1
				u3 = u0 & u1
				u4 = u0 &~ u1
				u5 = u0 ^ u1
				u6 = ~u0
				u7 = u0 + u1
				u8 = u0 - u1
				u9 = u0 >> u20
				u10 = u0 << u20
			''',
			{ 'u2' : (OP1 | OP2),
			'u3' : (OP1 & OP2),
			'u4' : (OP1 & ~OP2),
			'u5' : (OP1 ^ OP2),
			'u6' : 0xffffffff ^ OP1,
			'u7' : OP1 + OP2,
			'u8' : twos(OP1 - OP2) ,
			'u9' : OP1 >> 5,
			'u10' : (OP1 << 5) & 0xffffffff }, None, None, None)
	
	def test_immediateOps():
		OP1 = 0x19289adf
			 
		return ({ 'u0' : OP1 },
			'''
				u2 = 15
				cr30 = u2	; Enable all threads

				u2 = u0 | 233
				u3 = u0 & 233
				u4 = u0 &~ 233
				u5 = u0 ^ 233
				u6 = u0 + 233
				u7 = u0 + -233		; Negative immediate operand
				u8 = u0 - 233
				u9 = u0 >> 5
				u10 = u0 << 5
			''',
			{ 'u2' : (OP1 | 233),
			'u3' : (OP1 & 233),
			'u4' : (OP1 & ~233),
			'u5' : (OP1 ^ 233),
			'u6' : (OP1 + 233),
			'u7' : OP1 - 233,
			'u8' : OP1 - 233,
			'u9' : OP1 >> 5,
			'u10' : (OP1 << 5) & 0xffffffff }, None, None, None)
			
			
	# This mostly ensures we properly detect integer multiplies as long
	# latency instructions and stall the strand appropriately.
	def test_integerMultiply():
		return ({'u1' : 5, 'u2' : 7, 'u4' : 17},
			'''
				i0 = i1 * i2	; Ensure A instructions are marked as long latency
				i1 = i0 * 13	; Ensure scheduler resolves RAW hazard with i0
								; also ensure B instructions are marked as long latency
				i2 = i1			; RAW hazard with type B
				i4 = i4 + 1		; Ensure these don't clobber results
				i4 = i4 + 1
				i4 = i4 + 1
				i4 = i4 + 1
				i4 = i4 + 1
				i4 = i4 + 1
			''',
			{
				't0u0' : 35,
				't0u1' : 455,
				't0u2' : 455,
				't0u4' : 23
			}, None, None, None)	
	
			
	# Shifting mask test.  We do this multiple address modes,
	# since those have different logic paths in the decode stage
	def test_vectorMask():
		code = ''
		for x in range(16):
			code += '''
				u0 = 15
				cr30 = u0
			
				v1{u1} = v1 + 1
				v2{~u1} = v2 + 1
				v3{u1} = v3 + u2
				v4{~u1} = v4 + u2
				v5{u1} = v5 + v20
				v6{~u1} = v6 + v20
				v7 = v7 + 1				; No mask
				v8 = v8 + u2			; No mask
				v9 = v9 + v20			; No mask
				u1 = u1 >> 1			
			'''			
	
		result1 = [ x + 1 for x in range(16) ]
		result2 = [ 15 - x for x in range(16) ]
		result3 = [ 16 for x in range(16) ]
		return ({ 'u1' : 0xffff, 'u2' : 1, 'v20' : [ 1 for x in range(16) ]}, 
			code, {
			'u0' : None,
			'v1' : result1,
			'v2' : result2,
			'v3' : result1,
			'v4' : result2,
			'v5' : result1,
			'v6' : result2,
			'v7' : result3,
			'v8' : result3,
			'v9' : result3,
			'u1' : None }, None, None, None)
			
	def test_shuffle():
		src = allocateRandomVectorValue()
		indices = shuffleIndices()
		
		return ({
				'v3' : src,
				'v4' : indices
			},
			'''
				u0 = 15
				cr30 = u0	; enable all threads
			
				v2 = shuffle(v3, v4)
			''',
			{ 'v2' : [ src[index] for index in indices ], 'u0' : None }, 
			None, None, None)

	# Copy instruction, with an immediate operator and register-register
	# transfer
	def test_copy():
		return ({ 'u0' : 0x12345678 }, '''
			u1 = 15
			cr30 = u1	; Enable all threads
			
			s1 = s0
			s2 = 123
		''', { 'u1' : 0x12345678, 'u2' : 123 }, None, None, None)

	def test_countZeroes():
		return ({ 'u15' : 0xa5000000 }, '''
			u0 = 15
			cr30 = u0	; Enable all threads

			u1 = clz(u15)
			u2 = ctz(u15)
			u15 = u15 >> 1
			u3 = clz(u15)
			u4 = ctz(u15)
			u15 = u15 >> 1
			u5 = clz(u15)
			u6 = ctz(u15)
			u15 = u15 >> 10
			u7 = clz(u15)
			u8 = ctz(u15)
		''', {
			'u0' : None,
			'u1' : 0,
			'u2' : 24,
			'u3' : 1,
			'u4' : 23,
			'u5' : 2,
			'u6' : 22,
			'u7' : 12,
			'u8' : 12,
			'u15' : None
		}, None, None, None)
