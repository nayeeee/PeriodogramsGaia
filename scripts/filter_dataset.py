# filter dataset

# 1.- Extract N examples or all:
# * where pf or frequency is not null 
# * L points in each band 
# * average magnitude in band G < M
# * 

from astropy.table import Table

ruta_archivo = r"C:\Users\nayel\OneDrive\Documentos\PeriodogramsGaia\vari_rrlyrae-result.vot.gz"
tabla = Table.read(ruta_archivo, format="votable")
print(tabla.columns)

# TableColumns names=('solution_id','SOURCE_ID','pf','pf_error','p1_o','p1_o_error','epoch_g','epoch_g_error','epoch_bp','epoch_bp_error','epoch_rp','epoch_rp_error','epoch_rv','epoch_rv_error','int_average_g','int_average_g_error','int_average_bp','int_average_bp_error','int_average_rp','int_average_rp_error','average_rv','average_rv_error','peak_to_peak_g','peak_to_peak_g_error','peak_to_peak_bp','peak_to_peak_bp_error','peak_to_peak_rp','peak_to_peak_rp_error','peak_to_peak_rv','peak_to_peak_rv_error','metallicity','metallicity_error','r21_g','r21_g_error','r31_g','r31_g_error','phi21_g','phi21_g_error','phi31_g','phi31_g_error','num_clean_epochs_g','num_clean_epochs_bp','num_clean_epochs_rp','num_clean_epochs_rv','zp_mag_g','zp_mag_bp','zp_mag_rp','num_harmonics_for_p1_g','num_harmonics_for_p1_bp','num_harmonics_for_p1_rp','num_harmonics_for_p1_rv','reference_time_g','reference_time_bp','reference_time_rp','reference_time_rv','fund_freq1','fund_freq1_error','fund_freq2','fund_freq2_error','fund_freq1_harmonic_ampl_g','fund_freq1_harmonic_ampl_g_error','fund_freq1_harmonic_phase_g','fund_freq1_harmonic_phase_g_error','fund_freq1_harmonic_ampl_bp','fund_freq1_harmonic_ampl_bp_error','fund_freq1_harmonic_phase_bp','fund_freq1_harmonic_phase_bp_error','fund_freq1_harmonic_ampl_rp','fund_freq1_harmonic_ampl_rp_error','fund_freq1_harmonic_phase_rp','fund_freq1_harmonic_phase_rp_error','fund_freq1_harmonic_ampl_rv','fund_freq1_harmonic_ampl_rv_error','fund_freq1_harmonic_phase_rv','fund_freq1_harmonic_phase_rv_error','best_classification','g_absorption','g_absorption_error')



















