function obj = lgsu(varargin)
% LGSU - Constructor for LGSU.
% function obj = lgsu(varargin)

% WRITTEN BY       : Kenth Eng�, 1999 Mar.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

if nargin == 0,
  obj.field = 'C';
  obj.shape = [];
  obj.data  = [];
  obj = class(obj,'lgsu',liegroup);
  return;
end;

arg1 = varargin{1};
if nargin == 1,				% Single argument
  if isa(arg1,'lgsu'),			% Same class: Copy constructor.
    obj = arg1;
    return;
  elseif isinteger(arg1),		% Integer: obj with shape = arg1.
    obj.field = 'C';
    obj.shape = arg1;
    obj.data  = [];
    obj = class(obj,'lgsu',liegroup);
    return;
  end;
end;
 
arg2 = varargin{2};
if nargin == 2,                         % Two arguments.
  if (isinteger(arg1) & isstr(arg2)),
    if strcmp(arg2,'C'),
      obj.field = arg2;
      obj.shape = arg1;
      obj.data  = [];
      obj = class(obj,'lgsu',liegroup);
      return;
    else,
      error('The field must be ''C''!');
    end;
  end;
end;

% Other cases: Something is wrong!
error('Function is called with illegal arguments!');
return;
