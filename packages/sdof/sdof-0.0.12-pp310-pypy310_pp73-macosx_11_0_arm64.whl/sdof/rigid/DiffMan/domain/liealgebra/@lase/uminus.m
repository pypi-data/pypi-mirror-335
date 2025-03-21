function [w] = uminus(u)
% UMINUS - Unary minus in LASE.
% function [w] = uminus(u)

% WRITTEN BY : Kenth Eng�, 1998.01.27
% MODIFIED BY: Kenth Eng�, 1999.04.12

w = u;
w.data{1} = -u.data{1};
w.data{2} = -u.data{2};
return;
