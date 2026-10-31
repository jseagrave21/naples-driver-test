# 🇮🇹 NSA Naples AFI Driver's License Exam Prep

> **Interactive Study Simulator for the NAVSUPPACT Naples Area Orientation Driver's Exam**  
> *48 Questions • Maximum 2 Misses Allowed • 125 Official Road Signs & Rules*

---

## 🎯 Overview

Every service member, DoD civilian, and authorized dependent arriving at **Naval Support Activity (NSA) Naples** must pass the Allied Forces Italy (AFI) driver's examination during Area Orientation before receiving their driving permit and picking up their vehicle.

The exam has a strict failure threshold:
* **Format:** 48 Multiple-Choice Questions
* **Pass Requirement:** Minimum 46/48 correct
* **Failure Threshold:** **3 missed questions is an automatic failure**

Commercial driving apps in the App Store either test the Italian Ministry of Transport exam (in Italian with 30 True/False questions) or use generic military question banks riddled with errors.

This open-source project faithfully reproduces the official 2-page NAVSUPPACT Naples study guide with **crisp, accurate vector signage** and realistic multiple-choice traps based on real test feedback.

---

## 🚀 Live Access

Open the web app directly in any browser (no app download, installation, or account creation required):

👉 [**https://jseagrave21.github.io/naples-driver-test/**](https://jseagrave21.github.io/naples-driver-test/)

---

## ✨ Features

* **Official 48Q Exam Simulator:** Pulls 48 randomized questions without replacement. Features a live 3-dot strike counter and triggers an immediate warning banner if you hit the 3-miss failure limit.
* **Trap Drill Mode (42 High-Risk Signs):** Isolates look-alike pairs (e.g., *Priority to vehicles from opposite direction* vs. *Oncoming traffic must wait*, *Dangerous Downgrade* vs. *Upgrade*, *Maximum Weight* vs. *Weight per Axle*).
* **Realistic Exam Distractors:** Incorporates the tricky options seen on the actual test—such as offering *"Permitted"* options on signs that lack diagonal slashes.
* **Full 125-Sign Study Guide:** Interactive catalog of all signs from Page 1 and Page 2. Filter by category, search keywords, or enable **"Hide Labels"** mode to self-test with flashcards.
* **Persistent Weak Spots Deck:** Star any difficult sign, or let the app automatically save your missed questions to browser `localStorage` for targeted drill sessions.
* **Zero Dependencies / 100% Offline:** The entire app is self-contained in `index.html` using inline vector SVGs. It caches in browser memory and works without cell reception or Wi-Fi.

---

## 📱 Device Setup & Installation

The app is built as a responsive Progressive Web App (PWA) optimized for mobile and desktop screens.

### iPhone (Safari)
1. Navigate to `https://jseagrave21.github.io/naples-driver-test/` in **Safari**.
2. Tap the **Share** button (**⎋** / square with up arrow) in the bottom toolbar.
3. Scroll down and select **Add to Home Screen**.
4. Tap **Add**. The app will launch full-screen without Safari's browser navigation bars.

### Android / Pixel (Chrome)
1. Open the link in **Chrome**.
2. Tap the **three vertical dots (⋮)** in the upper-right corner.
3. Tap **Add to Home screen** (or **Install app**).
4. Launch from your app drawer or home screen for standalone offline study.

### MacBook / PC (Keyboard Hotkeys)
* **`1`, `2`, `3`, `4`** (or **`A`, `B`, `C`, `D`**): Select an answer option.
* **`Space`** or **`Enter`**: Advance to the next question immediately.
* **On macOS Sonoma+:** Click **File** in Safari $\rightarrow$ **Add to Dock...** to create a desktop app.

---

## ⚠️ Critical Study Traps to Watch Out For

Based on actual exam feedback, keep these key Vienna Convention rules in mind:

1. **No-Slash Prohibition Traps:**
   Under European road convention, a **red circular border alone denotes a prohibition**.
   * Signs like *Pedestrians Prohibited*, *Bicycles Prohibited*, *Motorcycles Prohibited*, and *All Motor Vehicles Prohibited* **do not have a diagonal slash**.
   * The real test includes options like *"Pedestrians Permitted"*—do not fall for it. Only *No Horn Blowing* and parking restrictions use diagonal slashes.

2. **Right-of-Way Arrow Colors:**
   * **Red Circle** with red right arrow + black left arrow = *Priority to vehicles from opposite direction* (You must yield).
   * **Blue Square** with white right arrow + red left arrow = *Oncoming traffic must wait* (You have priority).

3. **Permanent vs. Temporary Warnings:**
   * **White background triangle** = Permanent warning.
   * **Yellow background triangle** = Temporary warning (Work in progress / roadworks).

4. **The Four Foundational Shape Rules (Bottom of Page 2):**
   * *All Triangles* = Warning
   * *All Circles* = Prohibited
   * *All Blue Circles* = Mandatory
   * *Red and Yellow Triangles* = Temporary Warning

---

## 📁 Repository Structure

```text
├── index.html                   # Complete standalone web application & SVG sign engine
├── Drivers Study Guide.pdf      # Official 2-page NAVSUPPACT Naples handout
└── README.md                    # Project documentation & user guide
```

---

## 🤝 Community & Contributions

Built for incoming service members, civilians, and families stationed at NSA Naples (Capodichino & Gricignano Support Site).

Feel free to open an issue or submit a pull request if you spot an updated sign design, wording change, or want to contribute additional AFI question modules.

*Disclaimer: This study guide is an independent community preparation tool and is not officially affiliated with or endorsed by the U.S. Navy or NAVSUPPACT Naples.*
