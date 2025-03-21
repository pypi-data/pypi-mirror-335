function [] = dmex1a()
% DMEX1A - DiffMan example # 1a.
%
% DMEX1A:          This is an ODE evolving in SO(3)
% DOMAIN:          hmlie(lgso(3))
% ACTION:          Left multiplication of lgso(3) on itself
% GENERATOR MAP:   'vfex1'
% EQUATION TYPE:   'Linear'
%
% PURPOSE:         Integrate 'dmex1' with variable and constant stepsize.

clc
disp(' ');
disp('DMEX1A:          This is an ODE evolving in SO(3)');
disp('DOMAIN:          hmlie(lgso(3))');
disp('ACTION:          Left multiplication of lgso(3) on itself.');
disp('GENERATOR MAP:   ''vfex1''');
disp('EQUATION TYPE:   ''Linear''');
disp(' ');
disp('PURPOSE:         Integrate ''dmex1'' with variable and constant stepsize.');
disp(' ');
disp('Pause. Press any key to continue.');
pause

clc
disp(' ');
disp('Step #1: Construct an initial domain object in a homogeneous space:');
disp(' ');
y = hmlie(lgso(3));
setdata(y,eye(3));
y
disp(' ');
disp('Pause. Press any key to continue.');
pause

clc
disp(' ');
disp('Step #2: Construct a vectorfield object over the domain object:');
disp(' ');
vf = vectorfield(y);
setfm2g(vf,'vfex1');
seteqntype(vf,'L');
vf
disp(' ');
disp('Pause. Press any key to continue.');
pause

clc
disp(' ');
disp('Step #3: Construct a timestepper object:');
disp(' ');
ts = tsrkmk;
setcoordinate(ts,'pade22');
setmethod(ts,'RKF34');
ts
disp(' ');
disp('Pause. Press any key to continue.');
pause

clc
disp(' ');
disp('Step #4: Construct a flow object: ');
disp(' ');
f = flow;
settimestepper(f,ts);
setvectorfield(f,vf);
f
disp(' ');
disp('Pause. Press any key to continue.');
pause

tstart=0;
tend=3.0;

clc
disp(' ');
disp('Step #5: Solve the ODE using variable stepsize: ');
disp(' ');
disp('icur = f(y,0,3,-0.01);');
varstep=-1;  % use variable stepsize
fl1=flops;
icur = f(y,tstart,tend,varstep*0.01);
fl2=flops;
disp(' ');
disp(['     Number of flops used: ' num2str(fl2-fl1)]);
disp(' ');
disp('Pause. Press any key to continue.');
pause

clc
disp(' ');
disp('Step #5: Solve the ODE using constant stepsize: ');
disp(' ');
disp('icur = f(y,0,3,0.01);');
varstep=1;   % use constant stepsize
fl3=flops;
icurconst = f(y,tstart,tend,varstep*0.01);
fl4=flops;
disp(' ');
disp(['     Number of flops used: ' num2str(fl4-fl3)]);
disp(' ');
disp('Pause. Press any key to continue.');
pause

clc
disp(' ');
disp('Plotting results from the simulation:');
a = getdata(icur.y);
t = icur.t;
d = zeros(1,length(t));
for i = 1:size(a,3),
  d(i) = abs(det(a(:,:,i))-1);
end;
figure(1)
subplot(2,2,1);
plot(t,d);
xlabel('time');
ylabel('|det(solution)-1|');
title('Variable stepsize');

subplot(2,2,2);
plot(t(2:length(t)),diff(t));
xlabel('time');
ylabel('stepsize');
title('Stepsizes used throughout the integration process');

ac = getdata(icurconst.y);
tc = icurconst.t;
dc = zeros(1,length(tc));
for i = 1:size(ac,3),
  dc(i) = abs(det(ac(:,:,i))-1);
end;
subplot(2,2,3);
plot(tc,dc);
xlabel('time');
ylabel('|det(solution)-1|');
title('Constant stepsize');

disp('Done.');
disp(' ');
return;
