# Taxo — поточна контрольна точка

**Дата:** 08.11.2026  
**Stable / Latest:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10)  
**Stable exact source:** `6d0f32bc45323d4085bb165b2ec050dae7b378ee`  
**Поточний integrated main product:** **Taxo 10.13-r8** — owner manual-test candidate, не stable; exact product `78112c03db5406a2e4d9e4e4452226f6c9a82d0f`  
**Next code revision:** `10.13-r9` після feedback

## Поточний main після stable

У `main` інтегровано **10.13-r8**: безпечний масовий наказ про закріплення + автонумерація з r7. Exact-main: Windows #1329 — **987 tests / OK**, Win7 #315 — SUCCESS, macOS #1240 Intel/ARM — SUCCESS, START #2333 — SUCCESS.

Recovery-copy: `Taxo_CURRENT_MAIN_v10.13-r8_2026-11-08_START.zip`, 1 685 617 bytes, Drive file `1rj63QCtxmw4laO1KOnoVlx2PJoNccb20`, SHA256 `19cc825561f367afaa84d75cbc621dbd4767aa8f7bf284bd1d60a1a5cc35b61f`.

r7 safety mismatch закрито: one-driver→many-vehicles блокується ще до draft; допустимі bulk modes реально проходять чинний approval guard.

Це новіша розробка, але вона **не входить у stable 10.12-r10**.

## Далі

Наступний безпечний крок — **ручне приймання 10.13-r8 Windows Portable**: bulk assignment, autonumbering, personnel `-К`, valid approval і блокування one-driver→many-vehicles. Наступний code revision — **10.13-r9** тільки після feedback. Stable змінювати лише окремим рішенням власника.
