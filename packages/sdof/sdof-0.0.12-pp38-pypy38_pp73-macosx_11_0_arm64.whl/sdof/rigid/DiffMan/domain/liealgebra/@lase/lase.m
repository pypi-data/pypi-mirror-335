function obj = lase(varargin)
% LASE - Constructor for the Lie algebra LASE.
% function obj = lase(varargin)

% WRITTEN BY       : Kenth Eng�, 1998.01.16
% LAST MODIFIED BY : Kenth Eng�, 2000.03.29

%superiorto('lgse');

if nargin == 0,				% No args: Default constructor.
  obj.field = 'R';                      % Number field.
  obj.shape = [];
  obj.data  = {[] []};
  obj = class(obj,'lase',liealgebra);
  return;
end;

arg1 = varargin{1};
if nargin == 1,				% Single argument
  if isa(arg1,'lase'),			% Same class: Copy constructor.
    obj = arg1;
    return;
  elseif isinteger(arg1),		% Integer: obj with shape = arg1.
    obj.field = 'R';                    % Number field.
    obj.shape = arg1;
    obj.data  = {[] []};
    obj = class(obj,'lase',liealgebra);
    return;
  end;
end;

arg2 = varargin{2};
if nargin == 2,                         % Two arguments.
  if (isinteger(arg1) & isstr(arg2)),
    if strcmp(arg2,'R'),
      obj.field = arg2;
      obj.shape = arg1;
      obj.data  = [];
      obj = class(obj,'lase',liealgebra);
      return;
    else,
      error('The number field must be ''R''.');
    end;
  end;
end;
 
% Other cases: Something is wrong!
error('Function called with illegal arguments!');
return;
