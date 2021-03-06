-- oracle equivalent source sha1 c6ad0d5f2a3cf0c7825de2c4d68522736d56c0f8
-- retrieved from ./1241132947/9984c41fb98d15becf3c29432c19cd7a266dece4/schema/spacewalk/oracle/triggers/rhnErrataPackage.sql
--
-- Copyright (c) 2008--2010 Red Hat, Inc.
--
-- This software is licensed to you under the GNU General Public License,
-- version 2 (GPLv2). There is NO WARRANTY for this software, express or
-- implied, including the implied warranties of MERCHANTABILITY or FITNESS
-- FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
-- along with this software; if not, see
-- http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
-- 
-- Red Hat trademarks are not licensed under GPLv2. No permission is
-- granted to use or replicate Red Hat trademarks that are incorporated
-- in this software or its documentation. 
--
-- 
--
--
-- triggers for rhnErrataPackage

create or replace function rhn_errata_package_mod_trig_fun() returns trigger
as
$$
begin
        if tg_op='INSERT' or tg_op='UPDATE' then
                new.modified := current_timestamp;
	        return new;
        end if;
        if tg_op='DELETE' then
                update rhnErrata
                set rhnErrata.last_modified = current_timestamp
                where rhnErrata.id in ( old.errata_id );
	        return old;
        end if;
end;
$$ language plpgsql;




create trigger
rhn_errata_package_mod_trig
before insert or update or delete on rhnErrataPackage
for each row
execute procedure rhn_errata_package_mod_trig_fun();


