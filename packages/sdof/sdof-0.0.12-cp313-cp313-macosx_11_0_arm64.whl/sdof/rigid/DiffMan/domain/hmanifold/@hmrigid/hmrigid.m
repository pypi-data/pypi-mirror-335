function obj = hmrigid(varargin)
% HMRIGID - Constructor for HMRIGID-objects.
% function obj = hmrigid(varargin)
%
% DESCRIPTION:
%   Elements of HMRIGID are actually elements of the dual of the Lie algebra
%   of the Lie algebra LASO; that is LASO*.

% WRITTEN BY       : Kenth Eng�, 1998.09.15
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

superiorto('laso');

if nargin == 0,				% No arguments: Default constructor.
  obj.shape = [];
  obj.data  = [];
  obj = class(obj,'hmrigid',hmanifold);
  return;
end;

arg1 = varargin{1};
if nargin == 1,
  obj.shape = [];
  obj.data = [];
  obj = class(obj,'hmrigid',hmanifold);
  if isa(arg1,'hmrigid'),
    obj = arg1;
  elseif isinteger(arg1),
    obj.shape = laso(arg1); 
  elseif isa(arg1,'laso'),
    obj.shape = arg1; 
  else,
    error('Function called with illegal arguments!');
  end;
  return;
end;

% Other cases: Something is wrong!
error('Function called with illegal arguments!');
return;

