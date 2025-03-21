function z = zero(lalg)
% ZERO - Create the zero object in LASP.
% function z = zero(lalg)

% WRITTEN BY       : Hans Munthe-Kaas, 1997 March
% LAST MODIFIED BY : Kenth Eng�, 1999.04.06

n   = lalg.shape;
dat = zeros(n);
z   = lasp(lalg);
z.data = dat;
return;
