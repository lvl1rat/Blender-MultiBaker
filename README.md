# Multi Baker Addon for Blender

A **Blender Addon** designed to simplify and automate the process of baking multiple texture types (Diffuse, Normal, AO, etc.) onto a single image. It supports Smart UV mapping and lets you manage UV layers directly from the 3D Viewport UI.

⚠️ **Work In Progress** – Still under development. Expect bugs, missing features, and unoptimized logic. Feedback and contributions are welcome!

---

## ✨ Features

- Choose between existing UV maps or generate Smart UV maps.
- Support for baking multiple selected objects at once.
- Select from various bake types:
  - Diffuse, Normal, AO, Roughness, Emission, etc.
- Bake directly from the UI.
- Save baked images with auto-naming based on object and bake type.
- Lightweight panel in the **3D Viewport > Multi Baker** tab.

---

## 🧰 How to Use

1. **Install the Addon**:
   - In Blender, go to `Edit > Preferences > Add-ons > Install...`
   - Select the Python file and enable the addon.

   or

   - Go for the Script tab, paste it in and click run for a quick test.

3. **Set Up for Baking**:
   - In the 3D Viewport sidebar (`N` key), go to the **Multi Baker** tab.
   - Select the active or multiple objects.
   - Choose UV map or enable "Smart UV Map".
   - Select the bake type.
   - Create or select an image to bake into.

4. **Bake**:
   - Click **"Bake Texture"** to start the baking process.

5. **Save the Baked Image**:
   - After baking, click **"Save Image"** to export your result to a `.png` file.

---

## 🏗️ TODO

- Add auto image creation if none is assigned.
- Add progress indicators or status messages.
- Support exporting as JPG (currently set to PNG).
- Optional padding & margin control for UVs.
- Better error handling for missing UVs or images.

---

## 🐞 Known Issues

- No undo logic for automatic node creation.
- Image must be manually saved after baking if you don't use the "Save" button.

---

## 📄 License

MIT License

---

## ✍️ Author

**Bruno Franchini**  
🔗 [LinkedIn](https://www.linkedin.com/in/brfranch)
---

> _This is a personal tool built to support ongoing Blender projects, especially for streamlining texture baking workflows. Use at your own discretion!_
