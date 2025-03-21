function Value = get(sys,Property)
%GET  Access/query LTI property values.
%
%   VALUE = GET(SYS,'Property')  returns the value of the specified
%   property of the LTI model SYS.
%   
%   STRUCT = GET(SYS)  converts the TF, SS, or ZPK object SYS into 
%   a structure STRUCT with the property names as field names and
%   the property values as field values.
%
%   Without left-hand argument,  GET(SYS)  displays all properties 
%   of SYS and their values.
%
%   See also  SET, TFDATA, ZPKDATA, SSDATA.

%       Author(s): A. Potvin, 3-1-94
%       Revised: P. Gahinet, 4-1-96
%       Copyright (c) 1994 by The MathWorks, Inc.
%       $Revision: 1.1 $

ni = nargin;
no = nargout;
error(nargchk(1,2,ni));
if no>1,
   error('Too many output arguments.')
elseif ni==2 & ~isstr(Property) & ~iscellstr(Property),
   error('Input PROPERTY must be a string.');
end
sys = tf(sys);   % default method for TF children

% Get properties 
Props = pvpget('tf');

% Handle various cases
if ni==2,
   [ind,stat] = pmatch(Props,Property);
   error(stat);
   if length(ind)==1, 
      % Single property
      Property = Props{ind};
      switch Property
      case 'num'
         Value = sys.num;
      case 'den'
         Value = sys.den;
      case 'Variable'
         Value = sys.Variable;
      otherwise
         Value = get(sys.lti,Property);
      end
   else
      % List of properties
      PValues = [{sys.num ; sys.den ; sys.Variable};...
                                             struct2cell(sys.lti)];
      Value = PValues(ind)';
   end
else
   % All property values
   PValues = [{sys.num ; sys.den ; sys.Variable} ; ...
                                          struct2cell(sys.lti)];
   PValues = PValues(1:length(Props));
   if no,
      Value = cell2struct(PValues,Props,1);
   else
      pvpdisp(Props,PValues,' = ');
   end
end

% end ../@tf/get.m
