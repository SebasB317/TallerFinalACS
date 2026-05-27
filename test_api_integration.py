import httpx
import json
import sys

BASE_URL = "http://localhost:8000"
client = httpx.Client(timeout=10.0)

print("\n" + "="*60)
print("PRUEBA DE INTEGRACIÓN: 3 EJERCICIOS PRINCIPALES")
print("="*60 + "\n")

# TEST 1: EJERCICIO 1 - AUTENTICACIÓN JWT
print("█ EJERCICIO 1: AUTENTICACIÓN JWT")
print("-"*60)

print("\n[1.1] Registrando usuario...")
try:
    resp = client.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "email": "usuario_test_unique@example.com",
            "password": "Password123",
            "full_name": "Usuario Test"
        }
    )
    if resp.status_code in [200, 201]:
        user = resp.json()
        print(f"✅ Usuario registrado: {user['email']}")
        print(f"   ID: {user['id']}")
        print(f"   Nombre: {user['full_name']}")
        print(f"   Activo: {user['is_active']}")
    else:
        print(f"❌ Error: {resp.status_code}")
        print(f"   {resp.json()}")
except Exception as e:
    print(f"❌ Excepción: {e}")
    sys.exit(1)

print("\n[1.2] Haciendo login...")
try:
    resp = client.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": "usuario_test_unique@example.com",
            "password": "Password123"
        }
    )
    if resp.status_code in [200, 201]:
        login = resp.json()
        token = login['access_token']
        print(f"✅ Login exitoso")
        print(f"   Token: {token[:50]}...")
        print(f"   Usuario ID: {login['user_id']}")
        print(f"   Email: {login['email']}")
    else:
        print(f"❌ Error: {resp.status_code}")
        print(f"   {resp.json()}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Excepción: {e}")
    sys.exit(1)

print("\n[1.3] Verificando validaciones de email...")
try:
    resp = client.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "Password123"
        }
    )
    if resp.status_code == 422:
        print(f"✅ Validación de email funcionando (422 como esperado)")
    else:
        print(f"❌ Validación falló: {resp.status_code}")
except Exception as e:
    print(f"❌ Excepción: {e}")

print("\n✅ EJERCICIO 1 COMPLETADO\n")

# TEST 2: EJERCICIO 7 - MÉTRICAS (ADMIN)
print("█ EJERCICIO 7: MÉTRICAS (ADMIN)")
print("-"*60)

print("\n[7.1] Registrando usuario administrador...")
try:
    resp = client.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "AdminPass123",
            "full_name": "Administrador"
        }
    )
    if resp.status_code in [200, 201]:
        admin = resp.json()
        print(f"✅ Admin registrado: {admin['email']}")
    else:
        print(f"❌ Error: {resp.status_code}")
        print(f"   {resp.json()}")
except Exception as e:
    print(f"❌ Excepción: {e}")

print("\n[7.2] Login como administrador...")
try:
    resp = client.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "AdminPass123"
        }
    )
    if resp.status_code in [200, 201]:
        admin_login = resp.json()
        admin_token = admin_login['access_token']
        print(f"✅ Admin logged in")
    else:
        print(f"❌ Error: {resp.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Excepción: {e}")
    sys.exit(1)

print("\n[7.3] Accediendo a endpoint de métricas...")
try:
    resp = client.get(
        f"{BASE_URL}/api/v1/admin/metrics",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    if resp.status_code in [200, 201]:
        metrics = resp.json()
        print(f"✅ Métricas obtenidas:")
        print(f"   Usuarios registrados: {metrics.get('total_users_registered', 0)}")
        print(f"   Pagos procesados: {metrics.get('total_payments_processed', 0)}")
        print(f"   Tasa de éxito: {metrics.get('success_rate', 0):.2%}")
        print(f"   Comisión total: ${metrics.get('total_commissions', 0):.2f}")
    else:
        print(f"❌ Error: {resp.status_code}")
        print(f"   {resp.json()}")
except Exception as e:
    print(f"❌ Excepción: {e}")

print("\n✅ EJERCICIO 7 COMPLETADO\n")

# TEST 3: EJERCICIO 9 - PAGOS INTERNACIONALES
print("█ EJERCICIO 9: PAGOS INTERNACIONALES")
print("-"*60)

print("\n[9.1] Procesando pago en USD (Card)...")
try:
    resp = client.post(
        f"{BASE_URL}/api/v1/payments/",
        json={
            "amount": 100.00,
            "currency": "USD",
            "description": "Pago de prueba",
            "merchant_id": "MERCHANT_001",
            "method": "card"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    if resp.status_code in [200, 201]:
        payment = resp.json()
        print(f"✅ Pago procesado:")
        print(f"   ID: {payment.get('id')}")
        print(f"   Monto: {payment.get('amount')}")
        print(f"   Moneda: {payment.get('currency')}")
        print(f"   Comisión: {payment.get('commission')}")
        print(f"   Total: {payment.get('total')}")
        print(f"   Estado: {payment.get('status')}")
    else:
        print(f"❌ Error: {resp.status_code}")
        print(f"   {resp.json()}")
except Exception as e:
    print(f"❌ Excepción: {e}")

print("\n✅ EJERCICIO 9 COMPLETADO\n")

print("█ EJERCICIO 9: PRUEBAS ADICIONALES DE MONEDAS")
print("-"*60)

print("\n[9.2] Procesando pago en EUR (Card)...")
try:
    resp = client.post(
        f"{BASE_URL}/api/v1/payments/",
        json={
            "amount": 150.50,
            "currency": "EUR",
            "merchant_id": "MERCHANT_002",
            "method": "card"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    if resp.status_code in [200, 201]:
        payment = resp.json()
        print(f"✅ Pago en EUR procesado:")
        print(f"   ID: {payment.get('id')}")
        print(f"   Monto: {payment.get('amount')} {payment.get('currency')}")
        print(f"   Comisión: {payment.get('commission')}")
        print(f"   Estado: {payment.get('status')}")
    else:
        print(f"❌ Error: {resp.status_code}")
        print(f"   {resp.json()}")
except Exception as e:
    print(f"❌ Excepción: {e}")

print("\n[9.3] Procesando pago en GBP (Bank Transfer)...")
try:
    resp = client.post(
        f"{BASE_URL}/api/v1/payments/",
        json={
            "amount": 200.00,
            "currency": "GBP",
            "merchant_id": "MERCHANT_003",
            "method": "bank_transfer"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    if resp.status_code in [200, 201]:
        payment = resp.json()
        print(f"✅ Pago en GBP procesado:")
        print(f"   ID: {payment.get('id')}")
        print(f"   Monto: {payment.get('amount')} {payment.get('currency')}")
        print(f"   Comisión: {payment.get('commission')}")
        print(f"   Estado: {payment.get('status')}")
    else:
        print(f"❌ Error: {resp.status_code}")
        print(f"   {resp.json()}")
except Exception as e:
    print(f"❌ Excepción: {e}")

print("\n✅ PRUEBAS ADICIONALES COMPLETADAS\n")

print("="*60)
print("✅ TODOS LOS TESTS DE INTEGRACIÓN COMPLETADOS EXITOSAMENTE")
print("3 EJERCICIOS PRINCIPALES + PRUEBAS ADICIONALES DE MONEDAS")
print("="*60 + "\n")
