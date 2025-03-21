function obj = larn(varargin)
% LARN - Constructor for the Lie algebra LARN.
% function obj = larn(varargin)

% WRITTEN BY       : Kenth Eng�, 1997.09.10
% LAST MODIFIED BY : Kenth Eng�, 2000.03.29

%superiorto('lgrn');

if nargin == 0,
  obj.field = 'R';                     % Default number field.
  obj.shape = [];
  obj.data  = [];
  obj = class(obj,'larn',liealgebra);
  return;
end;

arg1 = varargin{1};
if nargin == 1,				% Single argument
  if isa(arg1,'larn'),			% Same class: Copy constructor.
    obj = arg1;
    return;
  elseif isinteger(arg1),		% Integer: obj with shape = arg1.
    obj.field = 'R';                     % Default number field.
    obj.shape = arg1;
    obj.data  = [];
    obj = class(obj,'larn',liealgebra);
    return;
  end;
end;

arg2 = varargin{2};
if nargin == 2,                         % Two arguments.
  if (isinteger(arg1) & isstr(arg2)),
    if strcmp(arg2,'R') | strcmp(arg2,'C'),
      obj.field = arg2;
      obj.shape = arg1;
      obj.data  = [];
      obj = class(obj,'larn',liealgebra);
      return;
    else,
      error('The number field must be: ''R'' or ''C''!');
    end;
  end;
end;
 
% Other cases: Something is wrong!
error('Function is called with illegal arguments!');
return;
