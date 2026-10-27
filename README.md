# exoplanet_transit_modeling
 | **`exoplanet_transit_modeling`** | Exoplanetary Kinematics | Non-Linear Least-Squares Inversion Fitting &amp; Keplerian Mechanics | `scipy.optimize`, `numpy` |
## Project 5: Exoplanetary Transit Photometry & Orbital Inversion Engine

### 1. Project Overview & Objective
Detecting extrasolar planetary systems relies heavily on transit photometry, measuring the slight dip in a star's brightness as a planet passes in front of it. By parsing the exact geometry of these light curves, astronomers can invert the observation problem to determine the planet's size, velocity, and distance from its parent star without ever seeing the planet directly.

This project is an automated exoplanetary analysis engine that processes high-cadence stellar flux timelines. The pipeline models non-linear brightness profiles across the stellar disk, removes observational sensor noise, fits physical light curves using Levenberg-Marquardt optimization algorithms, and solves Keplerian mechanics to calculate the planet's physical orbital radius.

---

### 2. Pipeline Architecture
The pipeline is designed using Object-Oriented Programming (OOP) in Python and handles heavy array processing completely via vectorized matrices.

The data flows through four distinct phases:
`[Telemetry Stream Generation] ──> [Stellar Limb-Darkening Correction] ──> [Non-Linear Inversion Fit] ──> [Keplerian Kinematics Solver]`

*   **Telemetry Generation:** Creates continuous 2-minute cadence observation data across a 48-hour tracking window (1,440 data rows), embedding Gaussian instrumentation white noise to replicate space-based assets like Kepler and TESS.
*   **Limb-Darkening Correction:** Computes brightness variations across the star's disk using an analytical quadratic profile. This adjusts for the fact that a star appears brighter at its center than at its edges.
*   **Inversion Fitting Engine:** Utilizes non-linear least-squares optimization loops (`scipy.optimize.curve_fit`) to match the noisy data array with a physical transit model, extracting the exact transit midpoint, duration, and depth drop.
*   **Keplerian Solver:** Takes the calculated light curve traits, assumes basic properties of a sun-like parent star, and processes the math to extract the planet's exact orbital separation in Astronomical Units (AU).

---

### 3. Core Math & Logic

#### Quadratic Limb-Darkening Approximation
A star's gas layer causes its outer edge to look cooler and darker than its center. The engine accounts for this variation across the stellar disk by calculating a continuous intensity correction factor at each step:

`Intensity_Correction = 1 - u1 * (1 - mu) - u2 * (1 - mu)^2`

Where `u1` and `u2` are fixed stellar limb-darkening constants (0.4 and 0.2), and `mu` is the cosine of the angle of incidence, derived from the planet's geometric radial distance `d` from the stellar center:

`mu = sqrt(1 - d^2)`

#### Non-Linear Inversion Modeling
The depth of the light curve dip does not scale linearly because the planet passes over regions of varying brightness on the star's surface. The engine solves this tracking challenge by running a Levenberg-Marquardt optimization loop. This algorithm systematically minimizes the variance between the observed telemetry data points and the physical transit model to determine the exact properties of the planet:

`Transit_Depth = (Rp / Rs)^2`

Taking the square root of the extracted depth calculates the true planet-to-star radius ratio (`Rp/Rs`). This lets you measure the physical radius of the hidden planet relative to its star.

#### Keplerian Orbital Reconstruction
Once the orbital period and stellar mass are defined, the engine applies Kepler's Third Law to calculate the absolute size of the planet's orbit (its semi-major axis, `a`):

`a = ((G * M * P^2) / (4 * pi^2)) ^ (1/3)`

*   **G:** Universal Gravitational Constant (6.6743e-11 m³ kg⁻¹ s⁻²)
*   **M:** Stellar Mass baseline (1.989e30 kg for a Sun-like star)
*   **P:** Orbital period converted into seconds (`3.52 days = 304,128 seconds`)

The engine calculates the final distance in meters, then divides the result by `1.496e11` to output a clean value in Astronomical Units (AU).

---

### 4. Output & Verification

Running the computational engine prints out an operational exoplanetary inversion log in the terminal:

```text
==================================================
        EXOPLANETARY ORBITAL INVERSION REPORT      
==================================================
Extracted Transit Depth : 1.440 %
Derived Radius Ratio (Rp/Rs) : 0.1200
Calculated Semi-Major Axis   : 0.0454 AU
Orbital Radial Distance      : 6793.81 x 10^6 km
==================================================
```

#### Diagnostic Graphics Analysis
The generated visual graph (`exoplanet_transit_kinematics.png`) confirms the physics model matches the raw data:
*   **Telemetry Scatter:** The grey data points replicate realistic, noisy space telescope readings, showing a clear dip during the transit window.
*   **Model Fit Line:** The bright cyan curve shows the optimized physical model fit. The curved shape at the bottom of the dip confirms the quadratic limb-darkening calculation is working correctly, capturing how the planet blocks varying amounts of light as it crosses the star's dark edges and bright center.

![Exoplanet Transit Output](exoplanet_transit_modeling/exoplanet_transit_kinematics.png)
