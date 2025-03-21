function [out] = fteff(flo,EX,y0,t0,tend,h0)
% FTEFF - This function computes the efficiency of a given method
%         solving a given problem
%
% CALLED AS:  out = fteff(flo,EX,y0,t0,tend,h0);
%           where
%             flo  - the flow object to estimate
%             EX   - the reference flow object (giving "exact" solution)
%                    or a precomputed exact solution
%             y0   - the initial data
%             t0   - (if specified) overrules the default value "tstart"
%             tend - (if specified) overrules the default value "tend"
%             h0   - (if specified) overrules the default value "stepsize"
%           and
%             out.fl=fl;       (number of flops used)
%             out.err=err;     (global error estimate)
%             out.sol=EXicur;  ("exact" solution - if computed)

% WRITTEN BY       : Arne Marthinsen, October 1998
% LAST MODIFIED BY : 

global DMARGCHK

if DMARGCHK
  if ~isa(flo,'flow'),
    error('First argument is not a flow object');
  end;
  if (~isa(EX,'flow') & ~isa(EX,'struct')),
    error('Second argument is not a flow object or a struct');
  end;
  if ((nargin < 3)|(nargout > 1)),
    error('Wrong number of input/output arguments!');
  end;
  if ~isa(y0,'hmanifold'),
    error('Third argument is no manifold object');
  end;
  if nargin > 3,
    if ~isreal(t0),
      error('t0 is a non-scalar argument');
    end;
    if nargin > 4,
      if ~isreal(tend),
	error('tend is a non-scalar argument');
      end;
      if nargin > 5,
	if ~isreal(h0),
	  error('h0 is a non-scalar argument');
	end;
      end;
    end;
  end;
end;

compex=0;

if isa(EX,'flow'),
  compex=1;
else
  EXicur=EX;
end;

% get values
def=getdefaults(flo);

% initialization
if nargin<4, t0=def.tstart; end;
if nargin<5, tend=def.tend; end;
if nargin<6, h=def.stepsize; else h=h0; end;

% declaration
err=zeros(def.numstep,1);
fl=zeros(def.numstep,1);

if def.disp,
  fprintf(1,'Computing global error versus flops:\n');
end;

if compex,
  % compute "exact" solution at t=tend
  if def.disp,
    fprintf(1,'   computing the "exact" solution...\n');
  end;
  EXicur=EX(y0,t0,tend,h/((2^def.numstep)*def.global));
end;

if def.disp,
  fprintf(1,'   looping %d times: ',def.numstep);
end;

for k=1:def.numstep
  h=h/2;
  if def.disp,
    fprintf(1,'%d ',k);
  end;

  tt=flops;
  icur=flo(y0,t0,tend,h);
  fl(k)=flops-tt;

  % compute the error
  tdiff=abs(icur.t(length(icur.t))-EXicur.t(length(EXicur.t)));
  if tdiff>100*eps,
    fprintf(1,['Warning: |tend_approx-tend_exact|=%6.4f. '...
	  'Error estimation may be wrong.\n'],tdiff);
  end;
  err(k)=dist(icur.y(length(icur.y)),EXicur.y(length(EXicur.y)));
end

out.fl=fl;
out.err=err;
if compex,
  out.sol=EXicur;
end;

if def.disp,
  fprintf(1,'\ndone fteff\n');
end;

return;
