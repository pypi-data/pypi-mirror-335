function obj = hmnsphere(varargin)
% HMNSPHERE - Constructor for HMNSPHERE-objects.
% function obj = hmnsphere(varargin)
%
% DESCRIPTION:
%      An N-sphere is turned into an homogeneous manifold, by the action of
%      laso - the Lie algebra of the Lie group O(n) that consists of
%      orthogonal matrices.  

% WRITTEN BY       : Kenth Eng�, 1997 Oct.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

superiorto('laso');

if nargin == 0,				% No arguments: Default constructor.
  obj.shape = [];
  obj.data = [];
  obj = class(obj,'hmnsphere',hmanifold);
  return;
end;

arg1 = varargin{1};
% Single argument of same class: Copy constructor
if nargin == 1,
  obj.shape = []; obj.data = [];
  obj = class(obj,'hmnsphere',hmanifold);
  if strcmp(class(arg1),'hmnsphere'),
    if ~isempty(arg1.shape), 		% Copy shape-info if non-empty.
      obj.shape = arg1.shape;
    end;
  elseif strcmp(class(arg1),'laso'),
    obj.shape = arg1;
  elseif isinteger(arg1),		% Integer input.
    la = laso(arg1);
    obj.shape = la;
  else,
    error('Function called with illegal arguments!');
  end;
  return;
end;

% Other cases: Something is wrong!
error('Function called with illegal arguments!');
return;

