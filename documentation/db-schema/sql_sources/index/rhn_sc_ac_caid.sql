-- created by Oraschemadoc Tue Nov  2 08:33:05 2010
-- visit http://www.yarpen.cz/oraschemadoc/ for more info

  CREATE INDEX "SPACEWALK"."RHN_SC_AC_CAID" ON "SPACEWALK"."RHNSERVERCHANNELARCHCOMPAT" ("CHANNEL_ARCH_ID") 
  PCTFREE 10 INITRANS 2 MAXTRANS 255 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "USERS" 
 
/