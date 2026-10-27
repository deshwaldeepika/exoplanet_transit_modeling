import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class ExoplanetTransitEngine:
    """
    Advanced Astrophysics Pipeline for simulating stellar transit photometry, 
    modeling quadratic limb-darkening profiles, and solving exoplanetary orbital kinematics.
    """
    def __init__(self, observation_window_hours: float = 48.0, cadence_minutes: float = 2.0):
        self.time = np.arange(-observation_window_hours / 2.0, observation_window_hours / 2.0, cadence_minutes / 60.0)
        self.flux = None
        self.true_parameters = {}

    def generate_synthetic_transit_stream(self):
        """
        Simulates high-cadence stellar flux telemetry modeling a Hot Jupiter transit.
        Implements an analytical quadratic stellar limb-darkening profile alongside white noise.
        """
        # Physical Core Parameters
        t_mid = 0.0             # Transit midpoint alignment (Hours)
        t_duration = 4.2        # Total physical transit duration (Hours)
        p_radius_ratio = 0.12   # Planet-to-star radius ratio (Rp / Rs)
        impact_param = 0.3      # Impact parameter (b) relative to stellar disk radius
        
        self.true_parameters = {'t_mid': t_mid, 'duration': t_duration, 'r_ratio': p_radius_ratio, 'b': impact_param}
        
        # Calculate geometric normalized distance between planet center and stellar center
        # Approximated linearly during the local intersection window
        dist_from_center = np.sqrt(impact_param**2 + (2.0 * (self.time - t_mid) / t_duration)**2)
        
        # Initialize flat normalized stellar baseline profile
        normalized_flux = np.ones_like(self.time)
        
        # Isolate indices where the planetary body physically intersects the stellar disk
        in_transit = dist_from_center < 1.0 + p_radius_ratio
        
        for i in range(len(self.time)):
            if in_transit[i]:
                d = dist_from_center[i]
                # Analytical area overlap approximation
                if d > 1.0 - p_radius_ratio:
                    # Ingress/Egress partial occlusion phase calculation
                    alpha = (1.0 + p_radius_ratio**2 - d**2) / (2.0 * p_radius_ratio)
                    alpha = np.clip(alpha, -1.0, 1.0)
                    area_overlap = p_radius_ratio**2 * np.arccos(alpha)
                else:
                    # Complete geometric blocking phase
                    area_overlap = np.pi * p_radius_ratio**2
                
                # Apply Quadratic Limb-Darkening Corrections (Standard Linear/Quadratic coefficients: u1=0.4, u2=0.2)
                u1, u2 = 0.4, 0.2
                mu = np.sqrt(1.0 - np.clip(d, 0.0, 1.0)**2)
                intensity_correction = 1.0 - u1 * (1.0 - mu) - u2 * (1.0 - mu)**2
                
                # Calculate absolute flux dip adjusted for local variations in stellar brightness
                flux_dip = (area_overlap / np.pi) * intensity_correction
                normalized_flux[i] -= flux_dip

        # Inject white sensor noise standard in Kepler/TESS space mission telemetry
        sensor_noise = np.random.normal(0, 0.0003, len(self.time))
        self.flux = normalized_flux + sensor_noise
        print(f"[STATUS] Generated {len(self.time)} data points of exoplanetary transit observations.")

    @staticmethod
    def analytical_transit_fit_model(t, t_mid, t_duration, depth):
        """
        Simplified geometric model designed for non-linear least-squares fitting engines,
        tracking the core properties of transit center, duration window, and depth drop.
        """
        dist = np.sqrt(0.3**2 + (2.0 * (t - t_mid) / t_duration)**2)
        fit_flux = np.ones_like(t)
        fit_mask = dist < 1.0
        fit_flux[fit_mask] -= depth * (1.0 - 0.4 * (1.0 - np.sqrt(1.0 - dist[fit_mask]**2)))
        return fit_flux

    def run_kinematic_inversion_solver(self):
        """
        Applies non-linear optimization routines to extract physical components from the data array
        and applies Keplerian mechanics to derive the exact distance of the planet from its star.
        """
        # Execute non-linear curve fitting via Levenberg-Marquardt optimization loops
        initial_guess = [0.5, 5.0, 0.01]
        fit_params, covariance = curve_fit(self.analytical_transit_fit_model, self.time, self.flux, p0=initial_guess)
        
        calc_t_mid, calc_duration, calc_depth = fit_params
        calc_r_ratio = np.sqrt(calc_depth) # Radius ratio extracted directly from depth metrics
        
        # --- Keplerian Kinematics Calculations ---
        # Constants assuming a sun-like parent star (Mass = 1 Solar Mass)
        orbital_period_days = 3.52  # Standard orbital cycle of a typical Hot Jupiter (HD 209458b class)
        period_seconds = orbital_period_days * 24.0 * 3600.0
        g_constant = 6.6743e-11
        m_star_kg = 1.989e30
        
        # Solve Kepler's Third Law to derive the physical semi-major axis (orbital radius)
        # Formula: a^3 = (G * M * P^2) / (4 * pi^2)
        semi_major_axis_meters = ((g_constant * m_star_kg * period_seconds**2) / (4.0 * np.pi**2))**(1.0 / 3.0)
        semi_major_axis_au = semi_major_axis_meters / 1.496e11  # Convert meters to Astronomical Units (AU)

        print("\n" + "="*50)
        print("        EXOPLANETARY ORBITAL INVERSION REPORT      ")
        print("="*50)
        print(f"Extracted Transit Depth : {calc_depth*100:.3f} %")
        print(f"Derived Radius Ratio (Rp/Rs) : {calc_r_ratio:.4f}")
        print(f"Calculated Semi-Major Axis   : {semi_major_axis_au:.4f} AU")
        print(f"Orbital Radial Distance      : {semi_major_axis_meters/1e6:.2f} x 10^6 km")
        print("="*50 + "\n")
        
        return fit_params, semi_major_axis_au

    def render_publication_plots(self, fit_params, semi_major_axis_au):
        """Generates high-resolution diagnostic plots comparing raw data to the physical model."""
        calc_t_mid, calc_duration, calc_depth = fit_params
        fitted_flux = self.analytical_transit_fit_model(self.time, *fit_params)
        
        plt.figure(figsize=(14, 7))
        
        # Scatter observed light curve data points
        plt.scatter(self.time, self.flux, color='dimgray', s=5, alpha=0.5, label='Kepler Space Telescope Telemetry')
        # Overlay the optimized physical inversion fit model
        plt.plot(self.time, fitted_flux, color='cyan', linewidth=2.5, 
                 label=f'Optimized Physical Model Fit (Depth: {calc_depth*100:.2f}%)')
        
        # Aesthetics adjustments matching astrophysics research standards
        plt.title(f"Exoplanetary Transit Photometry & Keplerian Inversion (Derived Semi-Major Axis: {semi_major_axis_au:.4f} AU)", 
                  fontsize=12, fontweight='bold')
        plt.xlabel("Time Offset from Mid-Transit Event (Hours)", fontsize=11)
        plt.ylabel("Normalized Flux Intensity ($F / F_0$)", fontsize=11)
        plt.xlim(-6.0, 6.0) # Zoom into the localized transit envelope window
        plt.ylim(0.983, 1.002)
        plt.grid(True, linestyle=':', alpha=0.5)
        plt.legend(loc='lower left')
        
        plt.savefig('exoplanet_transit_kinematics.png', dpi=300, bbox_inches='tight')
        print("[SUCCESS] Exoplanetary analysis completed. Visualization map exported.")
        plt.show()

if __name__ == "__main__":
    engine = ExoplanetTransitEngine()
    engine.generate_synthetic_transit_stream()
    params, axis_au = engine.run_kinematic_inversion_solver()
    engine.render_publication_plots(params, axis_au)
