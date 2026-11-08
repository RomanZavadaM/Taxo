# Taxo — поточна контрольна точка

**Дата:** 08.11.2026  
**Stable / Latest:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10)  
**Stable exact source:** `6d0f32bc45323d4085bb165b2ec050dae7b378ee`  
**Поточний integrated main product:** **Taxo 10.13-r7** — не stable; exact product `4c90082aba0aa3f1c7f4636466ceaa08aa541ecf`  
**Next code revision:** `10.13-r8`

## Поточний main після stable

У `main` інтегровано **10.13-r7**: масовий наказ про закріплення та дві незалежні серії автонумерації. Exact-main: Windows #1321 — **981 tests / OK**, Win7 #307 — SUCCESS, macOS #1232 Intel/ARM — SUCCESS, START #2331 — SUCCESS.

Recovery-copy: `Taxo_CURRENT_MAIN_v10.13-r7_2026-11-08_START.zip`, 1 680 167 bytes, Drive file `1lVmLFCqToh_9Bqhxrdd1e9Yuzz8Ol5r2`, SHA256 `09e0185d52dfbfd31c6745cf2afa31910be6a88645b18678eb95f683a8dbfea0`.

Відомий safety follow-up: режим «1 водій → кілька ТЗ» треба прибрати в r8 до owner package, бо чинний approval guard правильно блокує одночасне multi-vehicle assignment.

Це новіша розробка, але вона **не входить у stable 10.12-r10**.

## Далі

Наступний безпечний крок — **10.13-r8**: прибрати суперечливий режим «1 водій → кілька ТЗ» ще на етапі bulk selection, додати approval-regression, після exact-main дати owner Windows Portable для ручного приймання. Stable змінювати лише окремим рішенням власника.
