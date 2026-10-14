/*
 * =============================================================================
 * BIBLIOTECA C: SOLUCIONADORES NUMÉRICOS OPTIMIZADOS PARA EL MODELO COCLEAR
 * =============================================================================
 * Este archivo implementa rutinas numéricas críticas en C puro para obtener
 * rendimiento máximo. Son llamadas desde Python vía ctypes.
 *
 * La cóclea se modela como una LÍNEA DE TRANSMISIÓN ACOPLADA:
 * 1000 secciones conectadas en serie, donde cada sección representa una
 * porción de la membrana basilar con su propia frecuencia de resonancia.
 * Las ecuaciones diferenciales que gobiernan este sistema generan una
 * MATRIZ TRIDIAGONAL que debe resolverse en cada paso temporal de la
 * simulación (~100,000 veces por segundo de audio simulado).
 *
 * Funciones implementadas:
 *   - solve_tridiagonal: Eliminación gaussiana para matrices tridiagonales
 *     (algoritmo de Thomas). Resuelve el sistema de presiones acopladas
 *     entre secciones cocleares adyacentes.
 *   - delay_line: Línea de retardo con interpolación cúbica, implementa
 *     el mecanismo de "Zweig" que modela la reflexión de ondas dentro
 *     de la cóclea (responsable de las emisiones otoacústicas).
 *   - calculate_g: Calcula las fuerzas de amortiguamiento y rigidez
 *     que actúan sobre cada sección de la membrana basilar.
 * =============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#define PI 3.14159265358979323846

/*
 * Estructura que representa una matriz tridiagonal dispersa.
 * En el modelo coclear, esta matriz surge de la discretización espacial
 * de la ecuación de onda fluídica en la cóclea:
 *   - a[i]: acoplamiento con la sección coclear anterior (i-1)
 *   - b[i]: coeficiente diagonal (propiedades de la sección i)
 *   - c[i]: acoplamiento con la sección coclear siguiente (i+1)
 * La naturaleza tridiagonal refleja que cada sección de la membrana basilar
 * solo interactúa directamente con sus dos vecinas inmediatas a través
 * del fluido coclear (perilinfa) que las conecta.
 */
typedef struct tridiag_matrix{
	double *a;
	double *b;
	double *c;
} Tridiag_M;

/*
 * Interpolación lineal simple entre dos puntos.
 * Usada como fallback rápido cuando la interpolación cúbica no es necesaria.
 */
inline
double interpl_4(double a,double b,double c,double d,double frac){
    double cminusb = c-b;
    return b*(1-frac)+c*frac;
};

/*
 * Interpolación cúbica entre 4 puntos (Catmull-Rom).
 * Se usa para obtener valores intermedios de la línea de retardo de Zweig
 * con alta precisión. La interpolación cúbica es necesaria porque los
 * retardos cocleares no son múltiplos enteros del paso temporal, y
 * errores de interpolación se acumularían y generarían artefactos
 * numéricos audibles en las emisiones otoacústicas simuladas.
 */
double cubic_interpolate( float y0, float y1, float y2, float y3, float mu ) {
 
   double a0, a1, a2, a3, mu2;
 
   mu2 = mu*mu;
   a0 = y3 - y2 - y0 + y1; //p
   a1 = y0 - y1 - a0;
   a2 = y2 - y0;
   a3 = y1;
 
   return ( a0*mu*mu2 + a1*mu2 + a2*mu + a3 );
}

/*
 * Interpolación coseno entre dos puntos.
 * Variante suave que evita discontinuidades en la derivada.
 */
inline double cos_interpl(double a,double b,double frac){
    double mu2=(1-cos(frac*PI))/2;
    return a*(1-mu2)+b*mu2;
};

/*
 * solve_tridiagonal — Algoritmo de Thomas
 * =========================================
 * Resuelve el sistema lineal tridiagonal T·x = r, donde T es la matriz
 * tridiagonal que representa el acoplamiento fluídico entre secciones cocleares.
 *
 * Biología: En cada paso temporal, el modelo necesita calcular cómo la
 * presión del fluido coclear (perilinfa) se distribuye a lo largo de las
 * 1000 secciones de la cóclea. Las secciones están acopladas: el movimiento
 * de una sección desplaza fluido hacia sus vecinas. Este acoplamiento
 * genera un sistema de N ecuaciones lineales con estructura tridiagonal
 * que se resuelve eficientemente en O(N) operaciones.
 *
 * El vector solución x[i] contiene la presión diferencial (scala vestibuli
 * menos scala tympani) en cada sección, que es la fuerza que actúa sobre
 * la membrana basilar en esa posición.
 */
void solve_tridiagonal(Tridiag_M *t, double *r,double *x,int N) {
    int in;
    double *cprime=(double*) malloc(N*sizeof(double));
    /* Barrido hacia adelante (forward sweep): elimina la diagonal inferior */
    cprime[0] = t->c[0] / t->b[0];
    x[0] = r[0] / t->b[0];
 
    /* loop from 1 to N - 1 inclusive */
    for (in = 1; in < N; in++) {
        double m = 1.0 / (t->b[in] - t->a[in] * cprime[in - 1]);
        cprime[in] = t->c[in] * m;
        x[in] = (r[in] - t->a[in] * x[in - 1]) * m;
    }
    /* Barrido hacia atrás (back substitution): obtiene la solución final */
    /* loop from N - 2 to 0 inclusive, safely testing loop end condition */
    for (in = N - 1; in-- > 0; ){
        x[in] = x[in] - cprime[in] * x[in + 1]; /*wrong cprime[in] ebasta!*/
    }
        /* free scratch space */
 	free(cprime);
}

/*
 * delay_line — Línea de Retardo de Zweig con Interpolación Cúbica
 * ================================================================
 * Implementa el mecanismo de reflexión de ondas cocleares propuesto
 * por Zweig (1991). Modela cómo las ondas viajeras que se propagan
 * a lo largo de la membrana basilar son parcialmente reflejadas por
 * irregularidades microscópicas en la estructura coclear.
 *
 * Biología: La cóclea no es un tubo perfecto. Existen pequeñas
 * variaciones aleatorias en la rigidez, masa y geometría de la membrana
 * basilar. Estas irregularidades actúan como "espejos parciales" que
 * reflejan una fracción de la onda viajera de vuelta hacia la base.
 * Estas ondas reflejadas escapan por la ventana oval y se pueden medir
 * en el canal auditivo externo como EMISIONES OTOACÚSTICAS (OAE).
 *
 * El retardo de Zweig (Mu/f) representa el tiempo que tarda la onda
 * reflejada en viajar desde el sitio de reflexión de vuelta a la base.
 * Como este retardo generalmente no es un múltiplo entero del paso
 * temporal, se usa interpolación cúbica para obtener valores intermedios.
 *
 * Parámetros:
 *   Y:       Buffer circular con el historial de desplazamientos BM
 *   delay0-3: Índices de los 4 puntos para interpolación cúbica
 *   dev:     Fracción sub-muestral del retardo (0 < dev < 2)
 *   out:     Vector de salida: desplazamiento retardado de la BM (YZweig)
 *   M:       Longitud del buffer circular
 *   N:       Número de secciones cocleares
 */
void delay_line(double *Y, int *delay0,int *delay1,int *delay2,int *delay3,double *dev,double *out,int M,int N){
	int i;
	for(i=0;i<N;i++){
        int k=M*i;
        if(dev[i]<1){
        	out[i]=cubic_interpolate(Y[k+delay0[i]],Y[k+delay1[i]],Y[k+delay2[i]],Y[k+delay3[i]],dev[i]);
        }
        else{
        	out[i]=cubic_interpolate(Y[k+(delay0[i]+1)%M],Y[k+(delay1[i]+1)%M],Y[k+(delay2[i]+1)%M],Y[k+(delay3[i]+1)%M],dev[i]-1);
        }

	}
}

/*
 * calculate_g — Fuerzas sobre la Membrana Basilar
 * =================================================
 * Calcula el vector g[i] que contiene las fuerzas de amortiguamiento
 * y rigidez que actúan sobre cada sección de la membrana basilar.
 *
 * Biología:
 *   g[0]: Sección especial que representa la ventana oval / oído medio.
 *         La fuerza es proporcional a la velocidad del estribo (V[0]),
 *         escalada por la impedancia del oído medio (d_m_factor).
 *
 *   g[i] para i>0: Para cada sección coclear, la fuerza total tiene
 *         dos componentes:
 *         1. Amortiguamiento (sheraD): disipación de energía que controla
 *            la agudeza de la sintonización frecuencial. Depende del
 *            "polo de Shera" que determina el Q (factor de calidad) de
 *            cada sección. Las células ciliadas externas (OHC) modifican
 *            este parámetro activamente, implementando la amplificación
 *            coclear que da al oído humano su extraordinaria sensibilidad.
 *         2. Rigidez (omega²·Y + rho·YZweig): fuerza restauradora
 *            proporcional al desplazamiento. El término YZweig incorpora
 *            la retroalimentación retardada de Zweig (reflexiones internas).
 */
void calculate_g(double *V,double *Y,double *sherad_factor,double *sheraD,double *sheraRho,double *Yzweig,double *omega,double *g,double d_m_factor,const int n){
	int i;
	g[0]=d_m_factor*V[0];
	for(i=1;i<n;i++){
		g[i]=sherad_factor[i]*sheraD[i]*V[i]+omega[i]*omega[i]*(Y[i]+sheraRho[i]*Yzweig[i]);
	}
}
