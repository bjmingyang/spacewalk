-- created by Oraschemadoc Tue Nov  2 08:33:18 2010
-- visit http://www.yarpen.cz/oraschemadoc/ for more info

  CREATE OR REPLACE TRIGGER "SPACEWALK"."RHN_TEMPLATE_STR_MOD_TRIG" 
before insert or update on rhnTemplateString
for each row
begin
	:new.modified := sysdate;
end;
ALTER TRIGGER "SPACEWALK"."RHN_TEMPLATE_STR_MOD_TRIG" ENABLE
 
/
