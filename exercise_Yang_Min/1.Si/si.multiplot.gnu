#gnuplot
set terminal pngcairo size 1920,1080 font "Arial,20" dashed
set output 'multiplot.png'

#set label
set style fill solid 1.0 border lc rgb "black"
set key opaque
set key box lw 1 lc rgb "black"
set key font "Arial,24"           # font/size
set key textcolor rgb "black"  

set style line 1 lc rgb "gray" lt 1 lw 2
set style line 2 lc rgb "dark-blue" lt 3 lw 2
set style line 3 lc rgb "dark-red" lt 1 lw 2
set style line 4 lc rgb "dark-green" lt 1 lw 2

E_f =0
E_f1 = 6.1780 #pbesol
E_f2 = 6.1470 #ldaU 
E_f3 = 5.6673 #eACBN0 
E_f4 = 5.8507 #HSE 

ymin = -14 #-E_f1 
ymax = 8 #-E_f1
L = 0.0
G1 = 0.6124
X = 1.3195
U = 1.5695
G2 = 2.3195

set yrange[(E_f+ymin):(E_f+ymax)]
set xrange[0:G2]

set arrow from  L,  ymin+E_f to  L, ymax+E_f nohead
set arrow from  G1,  ymin+E_f to  G1, ymax+E_f nohead
set arrow from  X,  ymin+E_f to  X, ymax+E_f nohead
set arrow from  U,  ymin+E_f to  U, ymax+E_f nohead
set arrow from  G2,  ymin+E_f to  G2, ymax+E_f nohead
set xtics ("L" 0, "G" G1, "X" X, "U|K" U, "G" G2) 
shift= 2.3195/0.37949455E+01
plot "3.PBEsol/pp.out.gnu" u 1:($2-E_f1) w l ls 1 title '  PBEsol', "4.LDAU/pp.out.gnu" u 1:($2-E_f2) w l lt 2 lc rgb 'dark-blue' title '  LDA+U', "5.eACBN0/pp.out.gnu" u 1:($2-E_f3) w l ls 3 title '  eACBN0', "6.HSE/Si_band.dat" u ($1*shift):($2-E_f4) w l ls 4 title '  HSE' 

#pause -1
