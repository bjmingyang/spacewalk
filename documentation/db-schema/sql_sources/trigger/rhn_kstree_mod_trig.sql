-- created by Oraschemadoc Tue Nov  2 08:33:17 2010
-- visit http://www.yarpen.cz/oraschemadoc/ for more info

  CREATE OR REPLACE TRIGGER "SPACEWALK"."RHN_KSTREE_MOD_TRIG" 
before insert or update on rhnKickstartableTree
for each row
begin
     if (:new.cobbler_id = :old.cobbler_id) and
        (:new.cobbler_xen_id = :old.cobbler_xen_id) and
        (:new.last_modified = :old.last_modified) or
        (:new.last_modified is null ) then
             :new.last_modified := sysdate;
     end if;

	:new.modified := sysdate;
end rhn_kstree_mod_trig;
ALTER TRIGGER "SPACEWALK"."RHN_KSTREE_MOD_TRIG" ENABLE
 
/
