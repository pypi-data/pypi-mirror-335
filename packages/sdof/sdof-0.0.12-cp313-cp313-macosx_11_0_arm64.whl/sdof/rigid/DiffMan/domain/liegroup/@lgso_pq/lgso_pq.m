function obj = lgso_pq(varargin)
% LGSO_PQ - Constructor for Lie group LGSO_PQ.
% function obj = lgso_pq(varargin)

% WRITTEN BY       : Kenth Eng�, 1999 Apr.
% LAST MODIFIED BY : None

if nargin == 0,
  obj.field = 'R';
  obj.shape = [];
  obj.data  = [];
  obj = class(obj,'lgso_pq',liegroup);
  return;
end;

arg1 = varargin{1};
if nargin == 1,				% Single argument
  if isa(arg1,'lgso_pq'),		% Same class: Copy constructor.
    obj = arg1;
    return;
  elseif (isinteger(arg1) & (length(arg1) == 2) & all(arg1 > 0)),
    obj.field = 'R';
    obj.shape = arg1;
    obj.data  = [];
    obj = class(obj,'lgso_pq',liegroup);
    return;
  else,
    error('Argument must be an LGSO_PQ object or a positive integer 2-vector!');
  end;
end;
 
arg2 = varargin{2};
if nargin == 2,                         % Two arguments.
  if (isinteger(arg1) & isstr(arg2)) & (length(arg1) == 2) & all(arg1 > 0),
    if strcmp(arg2,'R'),
      obj.field = arg2;
      obj.shape = arg1;
      obj.data  = [];
      obj = class(obj,'lgso_pq',liegroup);
      return;
    else,
      error('The field must be ''R''!');
    end;
  else,
    error('Arg. 1 must be a positive integer 2-vector, and arg. 2 must be ''R''!');
  end;
end;

% Other cases: Something is wrong!
error('Function is called with illegal arguments!');
return;
