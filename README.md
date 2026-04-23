# WMESH

---

## 🇺🇸 English

**WMesh** is a Blender add-on for creating parametric primitives, inspired by the workflow in Cinema 4D. This is an updated version of the **W_Mesh_28x** add-on, fully compatible with **Blender 4.0 up to 5.1**.

### ✨ Features
* **Parametric Primitives:** Create Cube, Capsule, Cone, Plane, Disc, Screw, Sphere, Torus, and Cylinder (Pipe).
* **Section Support:** Create partial sections for Cylinder and Torus instead of full circles.
* **Full Control:** Adjust segments across all planes for every primitive.
* **[NEW] Shrinkage Compensation (Coef):** Available for rounded primitives (except Sphere/Screw). It compensates for size loss after applying the *Subdivision Surface* modifier for high-precision modeling.
* **[NEW] Improved Torus Modes:** Toggle between "Major Diameter/Section" and "Outer/Inner Diameter" for easier modeling from blueprints.
* **[NEW] Precision Workflow:** All rounded objects now use **Diameters** instead of Radii.

### 🚀 How to use
1. In Object Mode, press `Shift + A`.
2. Navigate to the **wPrimitives** menu and select a primitive.
3. Adjust parameters in the **Object Properties** panel.

> [!TIP]
> **About the "Coef" parameter:** It scales the object slightly so that after a *Subdivision Surface* modifier is applied, the object returns to its exact intended size. 
> *Note: Works only with even segment counts from 6 to 52 (currently in beta).*

**Important:** Once finished, click **"Convert to regular mesh"**. After conversion, parametric editing will no longer be available.

> [!CAUTION]
> Do not edit the primitive in *Edit Mode* before converting. Any changes made in Edit Mode will be reset if you adjust any parametric setting later!

---

## 🇷🇺 Русский

**WMesh** — плагин для Blender для создания параметрических примитивов аналогично тому, как это реализовано в Cinema 4D. Это обновленная версия плагина **W_Mesh_28x**, работающая в новых версиях **Blender от 4.0 до 5.1 включительно**.

### ✨ Возможности
* **Набор примитивов:** Куб, Капсула, Конус, Плоскость, Диск, Резьба, Сфера, Тор и Цилиндр (труба).
* **Работа с секциями:** Для Цилиндра или Тора можно создавать не только полные окружности, но и отдельные секции.
* **Детализация:** Гибкая настройка сегментов по всем плоскостям объектов.
* **[НОВОЕ] Коэффициент усадки (Coef):** Для всех округлых объектов (кроме Сферы/Резьбы). Позволяет сохранять точные размеры объекта после применения модификатора *Subdivision Surface*.
* **[НОВОЕ] Режимы Тора:** Переключение между режимами «Главный диаметр/Сечение» и «Внешний/Внутренний диаметр» для удобного моделирования по чертежам.
* **[НОВОЕ] Диаметры:** Все округлые объекты переведены с радиусов на диаметры.

### 🚀 Работа с плагином
1. В объектном режиме нажмите `Shift + A`.
2. Выберите нужный объект в меню **wPrimitives**.
3. Все настройки примитива находятся в панели **Object (Свойства объекта)**.

> [!TIP]
> **Параметр Coef:** Предназначен для компенсации усадки при сглаживании. При активации объект немного увеличится, а после применения *Subdivision Surface* примет точный размер. Работает при четном количестве сегментов от 6 до 52.

**Завершение работы:** После настройки нажмите кнопку **"Convert to regular mesh"**, чтобы преобразовать объект в обычную сетку. После этого редактирование параметров станет невозможным.

> [!CAUTION]
> **Внимание!** Не редактируйте примитив в *Edit Mode (Режим редактирования)* до конвертации. Любые изменения сетки будут сброшены, если вы измените любой параметр в панели настроек.

Приятного моделирования!