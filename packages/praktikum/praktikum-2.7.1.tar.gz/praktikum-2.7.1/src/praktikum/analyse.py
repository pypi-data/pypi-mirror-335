# -*- coding: utf-8 -*-

"""
Dieses Modul enthält grundlegende Funktionen, die bei der Datenanalyse im Grundpraktikum Physik
verwendet werden.
"""

import numpy as np
from numpy import sqrt,sin,cos,log,exp
import scipy.fft
import scipy.odr
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

from uncertainties import ufloat, correlated_values
import uncertainties.umath as um

def fit_ursprungsgerade(x, y, ey):
    '''
    Anpassung einer Ursprungsgerade.

    :param x: x-Werte der Datenpunkte
    :type x: array_like
    :param y: y-Werte der Datenpunkte
    :type y: array_like
    :param ey: Fehler auf die y-Werte der Datenpunkte
    :type ey: array_like

    Diese Funktion benötigt als Argumente drei Listen: x-Werte,
    y-Werte sowie eine mit den Fehlern der y-Werte.  Sie fittet eine
    Ursprungsgerade der Form :math:`y=ax` an die Werte und gibt die
    Steigung :math:`a` samt Unsicherheit sowie das :math:`\chi^2` aus.

    :rtype: Liste der Fit-Ergebnisse in der Reihenfolge [a, ea, chiq].

    '''

    sxx = sum(x**2/ey**2)
    sxy = sum(x*y/ey**2)
    a   = sxy / sxx
    ea  = 1. / sqrt(sxx)
    chiq = sum(((y-(a*x))/ey)**2)

    return a, ea, chiq


def lineare_regression(x,y,ey):
    '''
    Lineare Regression.

    :param x: x-Werte der Datenpunkte
    :type x: array_like
    :param y: y-Werte der Datenpunkte
    :type y: array_like
    :param ey: Fehler auf die y-Werte der Datenpunkte
    :type ey: array_like

    Diese Funktion benötigt als Argumente drei Listen: x-Werte,
    y-Werte sowie eine mit den Fehlern der y-Werte.  Sie fittet eine
    Gerade der Form :math:`y=ax+b` an die Werte und gibt die Steigung
    :math:`a` und y-Achsenverschiebung :math:`b` mit Fehlern sowie
    das :math:`\chi^2` und die Korrelation von :math:`a` und :math:`b`
    aus.

    :rtype: Liste der Fit-Ergebnisse in der Reihenfolge [a, ea, b, eb, chiq, corr].

    '''

    s   = sum(1./ey**2)
    sx  = sum(x/ey**2)
    sy  = sum(y/ey**2)
    sxx = sum(x**2/ey**2)
    sxy = sum(x*y/ey**2)
    delta = s*sxx-sx*sx
    b   = (sxx*sy-sx*sxy)/delta
    a   = (s*sxy-sx*sy)/delta
    eb  = sqrt(sxx/delta)
    ea  = sqrt(s/delta)
    cov = -sx/delta
    corr = cov/(ea*eb)
    chiq  = sum(((y-(a*x+b))/ey)**2)

    return a, ea, b, eb, chiq, corr


def lineare_regression_xy(x,y,ex,ey):
    '''
    Lineare Regression mit Fehlern in x und y.

    :param x: x-Werte der Datenpunkte
    :type x:  array_like
    :param y: y-Werte der Datenpunkte
    :type y:  array_like
    :param ex: Fehler auf die x-Werte der Datenpunkte
    :type ex:  array_like
    :param ey: Fehler auf die y-Werte der Datenpunkte
    :type ey:  array_like

    Diese Funktion benötigt als Argumente vier Listen: x-Werte,
    y-Werte sowie jeweils eine mit den Fehlern der x- und y-Werte.
    Sie fittet eine Gerade der Form :math:`y=ax+b` an die Werte und
    gibt die Steigung :math:`a` und y-Achsenverschiebung :math:`b` mit
    Fehlern sowie das :math:`\chi^2` und die Korrelation von :math:`a`
    und :math:`b` aus.

    Die Funktion verwendet den ODR-Algorithmus von scipy.

    :rtype: Liste der Fit-Ergebnisse in der Reihenfolge [a, ea, b, eb, chiq, corr].

    '''
    a_ini,ea_ini,b_ini,eb_ini,chiq_ini,corr_ini = lineare_regression(x,y,ey)

    def f(B, x):
        return B[0]*x + B[1]

    model  = scipy.odr.Model(f)
    data   = scipy.odr.RealData(x, y, sx=ex, sy=ey)
    odr    = scipy.odr.ODR(data, model, beta0=[a_ini, b_ini])
    output = odr.run()
    ndof = len(x)-2
    chiq = output.res_var*ndof
    corr = output.cov_beta[0,1]/np.sqrt(output.cov_beta[0,0]*output.cov_beta[1,1])

    # Es scheint, dass die sd_beta von ODR auf ein chi2/dof=1 reskaliert werden. Deshalb nehmen
    # wir den Fehler direkt aus der Kovarianzmatrix.
    return output.beta[0], np.sqrt(output.cov_beta[0,0]), output.beta[1], np.sqrt(output.cov_beta[1,1]), chiq, corr


def quadratische_regression(x, y, ey):
    '''
    Quadratische Regression mit Fehlern in y-Richtung.

    :param x: x-Werte der Datenpunkte
    :type x:  array_like
    :param y: y-Werte der Datenpunkte
    :type y:  array_like
    :param ey: Fehler auf die y-Werte der Datenpunkte
    :type ey:  array_like

    Diese Funktion benötigt als Argumente drei Listen:
    x-Werte, y-Werte sowie eine mit den Fehlern der y-Werte.

    Sie fittet eine Parabel der Form :math:`y=ax^2+bx+c` an die Werte und gibt die
    Parameter a, b und c mit Fehlern
    sowie das :math:`\chi^2` und die drei Korrelationskoeffizienten der Parameter aus.

    :rtype: Liste der Fit-Ergebnisse in der Reihenfolge [a, ea, b, eb, c, ec, chiq, (corr_ab, corr_ac, corr_bc)].
    '''

    p, V = np.polyfit(x, y, 2, w=1./ey, cov=True)

    corr = (V[0,1]/np.sqrt(V[0,0]*V[1,1]),
            V[0,2]/np.sqrt(V[0,0]*V[2,2]),
            V[1,2]/np.sqrt(V[1,1]*V[2,2]))
    chiq = np.sum(((y - (p[0]*x**2 + p[1]*x + p[2])) / ey)**2)

    return p[0], np.sqrt(V[0,0]), p[1], np.sqrt(V[1,1]), p[2], np.sqrt(V[2,2]), chiq, corr


def quadratische_regression_xy(x, y, ex, ey):
    '''
    Quadratische Regression mit Fehlern in x und y.

    :param x: x-Werte der Datenpunkte
    :type x:  array_like
    :param y: y-Werte der Datenpunkte
    :type y:  array_like
    :param ex: Fehler auf die x-Werte der Datenpunkte
    :type ex:  array_like
    :param ey: Fehler auf die y-Werte der Datenpunkte
    :type ey:  array_like

    Diese Funktion benötigt als Argumente vier Listen:
    x-Werte, y-Werte sowie jeweils eine mit den Fehlern der x-
    und y-Werte.
    Sie fittet eine Parabel der Form :math:`y=ax^2+bx+c` an die Werte und gibt die
    Parameter a, b und c mit Fehlern
    sowie das :math:`\chi^2` und die drei Korrelationskoeffizienten der Parameter aus.


    Die Funktion verwendet den ODR-Algorithmus von scipy.

    :rtype: Liste der Fit-Ergebnisse in der Reihenfolge [a, ea, b, eb, c, ec, chiq, (corr_ab, corr_ac, corr_bc)].

    '''

    # Startwerte (ignorieren den x-Fehler)
    p_ini = np.polyfit(x, y, 2, w=1./ey)

    def f(B, x):
        return B[0]*x**2 + B[1]*x + B[2]

    model  = scipy.odr.Model(f)
    data   = scipy.odr.RealData(x, y, sx=ex, sy=ey)
    # Reihenfolge der Startparameter muss invertiert werden.
    odr    = scipy.odr.ODR(data, model, beta0=p_ini[::-1])
    output = odr.run()
    ndof = len(x)-3
    chiq = output.res_var*ndof
    corr = (output.cov_beta[0,1]/np.sqrt(output.cov_beta[0,0]*output.cov_beta[1,1]),
            output.cov_beta[0,2]/np.sqrt(output.cov_beta[0,0]*output.cov_beta[2,2]),
            output.cov_beta[1,2]/np.sqrt(output.cov_beta[1,1]*output.cov_beta[2,2]))

    # Es scheint, dass die sd_beta von ODR auf ein chi2/dof=1 reskaliert werden. Deshalb nehmen
    # wir den Fehler direkt aus der Kovarianzmatrix.
    return output.beta[0], np.sqrt(output.cov_beta[0,0]), output.beta[1], np.sqrt(output.cov_beta[1,1]), output.beta[2], np.sqrt(output.cov_beta[2,2]), chiq, corr


def fourier(t,y):
    '''
    Fourier-Transformation.

    :param t: Zeitwerte der Datenpunkte
    :type t: array_like
    :param y: y-Werte der Datenpunkte
    :type y: array_like

    :rtype: Gibt das Fourierspektrum in Form zweier Listen (freq,amp) \
    zurück, die die Fourieramplituden als Funktion der zugehörigen \
    Frequenzen enthalten.
    '''

    assert(len(t) == len(y))
    dt = (t[-1]-t[0])/(len(t)-1)
    fmax = 0.5/dt
    step = fmax/len(t)
    freq=np.arange(0.,fmax,2.*step)
    amp = np.zeros(len(freq))
    i=0
    for f in freq:
        omega=2.*np.pi*f
        sc = sum(y*cos(omega*t))/len(t)
        ss = sum(y*sin(omega*t))/len(t)
        amp[i] = sqrt(sc**2+ss**2)
        i+=1
    return (freq,amp)


def fourier_fft(t, y):
    '''
    Schnelle Fourier-Transformation.

    :param t: Zeitwerte der Datenpunkte
    :type t: array_like
    :param y: y-Werte der Datenpunkte
    :type y: array_like

    :rtype: Gibt das Fourierspektrum in Form zweier Listen (freq,amp) \
    zurück, die die Fourieramplituden als Funktion der zugehörigen \
    Frequenzen enthalten.
    '''

    assert(len(t) == len(y))
    nt = len(t)
    dt = (t[-1] - t[0]) / (nt - 1)
    amp = abs(scipy.fft.rfft(y, norm='forward'))
    freq = scipy.fft.rfftfreq(nt, dt)
    return (freq, amp)


def exp_einhuellende(t,y,ey,sens=0.1):
    '''
    Exponentielle Einhüllende.

    :param t: Zeitwerte der Datenpunkte
    :type t: array_like
    :param y: y-Werte der Datenpunkte
    :type y: array_like
    :param ey:
    :type ey: array_like
        Fehler auf die y-Werte der Datenpunkte
    :param sens: Sensitivität, Wert zwischen 0 und 1
    :type sens: float, optional

    Die Funktion gibt auf der Basis der drei Argumente (Listen
    mit t- bzw. dazugehörigen y-Werten plus y-Fehler) der Kurve die
    Parameter A0 und delta samt Fehlern der Einhüllenden von der Form
    :math:`A=A_0\exp(-\delta{}t)` (abfallende Exponentialfunktion) als Liste aus.
    Optional kann eine Sensitivität angegeben werden, die bestimmt,
    bis zu welchem Prozentsatz des höchsten Peaks der Kurve
    noch Peaks für die Berechnung berücksichtigt werden
    (voreingestellt: 10%).

    :rtype: Liste [A0, sigmaA0, delta, sigmaDelta]

    '''
    if not 0.<sens<1.:
        raise ValueError(u'Sensitivität muss zwischen 0 und 1 liegen!')

    # Erstelle Liste mit ALLEN Peaks der Kurve
    Peaks=[]
    PeakZeiten=[]
    PeakFehler=[]
    GutePeaks=[]
    GutePeakZeiten=[]
    GutePeakFehler=[]
    if y[0]>y[1]:
        Peaks.append(y[0])
        PeakZeiten.append(t[0])
        PeakFehler.append(ey[0])
    for i in range(1,len(t)-1):
        if y[i] >= y[i+1] and \
           y[i] >= y[i-1] and \
           ( len(Peaks)==0 or y[i] != Peaks[-1] ): # handle case "plateau on top of peak"
           Peaks.append(y[i])
           PeakZeiten.append(t[i])
           PeakFehler.append(ey[i])

    # Lösche alle Elemente die unter der Sensitivitätsschwelle liegen
    Schwelle=max(Peaks)*sens
    for i in range(0,len(Peaks)):
        if Peaks[i] > Schwelle:
            GutePeaks.append(Peaks[i])
            GutePeakZeiten.append(PeakZeiten[i])
            GutePeakFehler.append(PeakFehler[i])

    # Transformiere das Problem in ein lineares
    PeaksLogarithmiert = log(np.array(GutePeaks))
    FortgepflanzteFehler = np.array(GutePeakFehler) / np.array(GutePeaks)
    LR = lineare_regression(np.array(GutePeakZeiten),PeaksLogarithmiert,FortgepflanzteFehler)

    A0=exp(LR[2])
    sigmaA0=LR[3]*exp(LR[2])
    delta=-LR[0]
    sigmaDelta=LR[1]
    return(A0,sigmaA0,delta,sigmaDelta)


def fit_gedaempfte_schwingung(t, y, ey, plot_fit=False, einheit_x='s', symbol_y='y', einheit_y='[y]', fehler_skalierung=False, fig_name=None):
    '''
    Fit einer gedämpften Schwingung (mit Offset) an Datenpunkte als Funktion der Zeit.

    Die Funktion passt auf der Basis der drei Argumente (Listen
    mit t- und dazugehörigen y-Werten plus y-Fehler) eine exponentiell
    gedämpfte Schwinung (einschließlich eines Offsets) der Form
    :math:`y=A\exp(-\delta{}t)\cos(2\pi{}t/T+\phi) + y_0`
    mit der Methode der kleinsten Quadrate an die Datenpunkte an.
    Die Startwerte werden automatisch bestimmt.

    Auf Wunsch werden die Datenpunkte und die angepasste Kurve zusammen mit einem
    Residuenplot in einer neuen Abbildung geplottet.

    :param t: Zeitwerte der Datenpunkte
    :type t: array_like
    :param y: y-Werte der Datenpunkte
    :type y: array_like
    :param ey: Fehler auf die y-Werte der Datenpunkte
    :type ey: array_like
    :param plot_fit: Sollen Datenpunkte, Fit und Residuenplot geplottet werden?
    :type plot_fit: bool
    :param einheit_x: Einheit der Zeit-Achse (für den Plot)
    :type einheit_x: str
    :param symbol_x: Formelzeichen für die Größe auf der y-Achse (für den Plot)
    :type symbol_x: str
    :param einheit_y: Einheit der y-Achse (für den Plot)
    :type einheit_y: str
    :param fehler_skalierung: Option, um die Unsicherheiten auf die Fit-Parameter so zu skalieren,
                              dass sie den Werten entsprechen, die man erhalten würde, wenn man die Unsicherheiten
                              auf die y-Werte so skaliert, dass man ein reduziertes Chi-Quadrat von 1 erhält.
                              Nützlich für die Bestimmung von systematischen Unsicherheiten.
    :type fehler_skalierung: bool
    :param fig_name: Name für die Abbildung
    :type fig_name: str oder None
    :return: Amplitude :math:`A`, Periodendauer :math:`T`, Phase :math:`\phi`, Dämpfungskonstante :math:`\delta`, Offset :math:`y_0`,
                       entsprechende Periodendauer der ungedämpften Schwingung :math:`T_0` (berechnet aus :math:`\omega^2=\omega_0^2-\delta^2`), :math:`\chi^2` der Anpassung, Anzahl der Freiheitsgrade
    :rtype: Tupel. Die Fit-Parameter werden als `ufloat` Objekte (Werte mit Unsicherheiten, aus dem `uncertainties` Paket) zurückgegeben.
    '''

    assert len(t) == len(y)
    assert len(y) == len(ey)

    # model definition: exponentially damped oscillation + constant offset
    model = lambda x, amp, T, phase, delta, p0: p0 + amp * np.exp(-delta*x) * np.cos(2.*np.pi/T * x + phase)

    # rough offset correction for Fourier analysis
    offset = np.mean(y)
    y_corr = y - offset

    # Fourier analysis for initial value of frequency
    fft_freq, fft_amp = fourier_fft(t, y_corr)
    f_fft = peakfinder_schwerpunkt(fft_freq, fft_amp)
    T_fft = 1.0 / f_fft

    # simple exponential envelope for start value of delta
    einh = exp_einhuellende(t, y_corr, ey)
    delta_start = einh[2]

    # initial values for model fit
    p0 = [np.max(y)-offset, T_fft, -2.*np.pi * t[np.argmax(y)] / T_fft, delta_start, offset]

    # non-linear fit of model to data and extraction of parameter uncertainties
    popt, pcov = curve_fit(model, t, y, p0=p0, sigma=ey, absolute_sigma=True)
    perr = np.sqrt(np.diag(pcov))

    # calculate chi2 from model fit
    chi2 = np.sum(((y - model(t, *popt)) / ey)**2)
    dof = len(t) - 5
    scaling_factor = 1.0
    if fehler_skalierung:
        scaling_factor = np.sqrt(chi2/dof)

    amp_fit, T_fit, phase_fit, delta_fit, y_offset = correlated_values(popt, pcov * scaling_factor**2)

    # gedämpfte Schwingung: omega_d^2 = omega_0^2 - delta^2
    # aber omega_0 ist die Kreisfrequenz, für die die meisten Herleitungen gelten
    omega_fit = 2.*np.pi / T_fit
    omega_0 = um.sqrt(omega_fit**2 + delta_fit**2)
    T_0 = 2.*np.pi / omega_0

    # prepare plot of model curve
    if plot_fit:
        xx = np.linspace(t[0] - 0.01, t[-1] + 0.01, 10000)
        model_pred = model(xx, *popt)

        # plot data and best-fit model, and residual plot below
        fig, ax = plt.subplots(2, 1, num=fig_name, sharex=True, gridspec_kw={'height_ratios': [5, 2]}, layout='tight')
        ax[0].plot(xx, model_pred, 'r-')
        ax[0].errorbar(t, y, yerr=ey, fmt='bo', markersize=5.0)
        ax[0].minorticks_on()
        ax[0].grid()
        ax[0].set_ylabel(f'${symbol_y}$ / {einheit_y}')
        ax[1].axhline(y=0., color='black', linestyle='--')
        ax[1].errorbar(t, y - model(t, *popt), yerr=ey, fmt='o', color='red', markersize=5.0)
        ax[1].set_xlabel(f'$t$ / {einheit_x}')
        ax[1].set_ylabel(f'$(({symbol_y})_{{i}}-f(t_i))$ / {einheit_y}')
        ymax = max([abs(x) for x in ax[1].get_ylim()])
        ax[1].set_ylim(-ymax, ymax)
        ax[1].minorticks_on()

        # text box with fit results
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        lines = [f'T = ({T_fit}) {einheit_x}',
                 fr'$\delta$ = ({delta_fit}) / {einheit_x}',
                 fr'$\mathregular{{T}}_\mathregular{{0}}$ = ({T_0}) {einheit_x}',
                 f'offset = ({y_offset}) {einheit_y}',
                 f'amp    = ({amp_fit}) {einheit_y}']
        if fehler_skalierung:
            lines.append('(Fehler skaliert)')
        lines.append(fr'$\chi^2$/df={chi2:.1f}/{dof:d}={chi2/dof:.1f}')
        lines = [x.replace('+/-', r'$\pm$') for x in lines]
        textstr = '\n'.join(lines)
        ax[0].text(0.85, 0.95, textstr, transform=ax[0].transAxes, fontsize=12,
                   verticalalignment='top', bbox=props)

        fig.subplots_adjust(hspace=0.0)

    return amp_fit, T_fit, phase_fit, delta_fit, y_offset, T_0, chi2, dof



def untermenge_daten(x,y,x0,x1):
    '''
    Extrahiere kleinere Datensätze aus (x,y), so dass x0 <= x <= x1

    :param x: x-Werte des Eingangsdatensatzes
    :type x: array_like
    :param y: Zugehörige y-Werte.
    :type y: array_like
    :param x0: x-Wert, ab dem die Daten extrahiert werden sollen.
    :type x0: float
    :param x1: x-Wert, bis zu dem die Daten extrahiert werden sollen.
    :type x1: float

    :rtype: (xn,yn) wobei xn und yn die reduzierten x- und y-Listen sind.
    '''
    xn=[]
    yn=[]
    for i,v in enumerate(x):
        if x0<=v<=x1:
            xn.append(x[i])
            yn.append(y[i])

    return (np.array(xn),np.array(yn))

def peak(x,y,x0,x1):
    '''
    Approximiere ein lokales Maximum in den Daten (x,y) zwischen x0 und x1. Die Quadrate der y-Werte werden
    dabei als Gewichte verwendet.

    :param x: x-Werte des Eingangsdatensatzes
    :type x: array_like
    :param y: Zugehörige y-Werte.
    :type y: array_like
    :param x0: Untergrenze für die Lages des Maximums
    :type x0: float
    :param x1: Obergrenze für die Lages des Maximums
    :type x1: float

    :rtype: Approximierte Lage des Maximums entlang x.
    '''
    N = len(x)
    i1 = 0
    i2 = N-1
    for i in range(N):
       if x[i] >= x0:
         i1 = i
         break
    for i in range(N):
       if x[i] > x1:
         i2 = i
         break

    if i2 == i1:
        i2 = i1 + 1

    sum_y = sum(y[i1:i2]**2)
    sum_xy = sum(x[i1:i2] * y[i1:i2]**2)
    xm = sum_xy / sum_y
    return xm

def peakfinder_schwerpunkt(x, y, schwelle=0.1):
    '''
    Finde Peak in den Daten (x,y) mit der Schwerpunktsmethode. Die Quadrate der y-Werte werden
    dabei als Gewichte verwendet. Es werden alle Datenpunkte verwendet, deren Amplitude oberhalb der
    gegebenen relativen Schwelle rund um das Maximum liegen.

    :param x: x-Werte des Eingangsdatensatzes.
    :type x: array_like
    :param y: Zugehörige y-Werte.
    :type y: array_like
    :param schwelle: Berechne Peak aus allen Datenpunkten, deren Amplitude mindestens :math:`schwelle\cdot\mathrm{max}(y)` beträgt.
    :type schwelle: float, optional

    :rtype: Lage des Maximums entlang x.
    '''
    N = len(x)
    i0 = 0
    i1 = N - 1
    ymax = max(y)
    for i in range(N):
        if y[i] > ymax * schwelle:
            i0 = i
            break
    for i in range(i0 + 1, N):
        if y[i] < ymax * schwelle:
            i1 = i - 1
            break
    xpeak = peak(x, y, x[i0], x[i1])
    return xpeak


def gewichtetes_mittel(y,ey):
    '''
    Berechnet den gewichteten Mittelwert der gegebenen Daten.

    :param y: Datenpunkte
    :type y: array_like
    :param ey: Zugehörige Messunsicherheiten.
    :type ey: array_like

    :rtype: Gibt den gewichteten Mittelwert samt Fehler als Tupel (Mittelwert, Fehler) zurück.
    '''
    w = 1/ey**2
    s = sum(w*y)
    wsum = sum(w)
    xm = s/wsum
    sx = sqrt(1./wsum)

    return (xm,sx)


def mittelwert_stdabw(daten):
    '''
    Berechnet das arithmetische Mittel und die empirische Standardabweichung der gegebenen Daten.

    Der Mittelwert der Daten :math:`\{x_1, \ldots, x_N\}` ist definiert als
    :math:`\overline{x} = \sum\limits_{i=1}^N x_i`. Die Standardabweichung ist gegeben durch
    :math:`\sigma_x = \sqrt{\\frac{1}{N-1} \sum\limits_{i=1}^N (x_i-\\bar{x})^2}`.

    :param daten: Messwerte
    :type daten: array_like

    :rtype: Tupel (Mittelwert, Standardabweichung)
    '''

    return (np.mean(daten), np.std(daten, ddof=1))
