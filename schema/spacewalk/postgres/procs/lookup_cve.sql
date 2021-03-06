-- oracle equivalent source sha1 f8ec6c07d6f4276d821e52bcacf61f2e930a8ba9
-- retrieved from ./1241042199/53fa26df463811901487b608eecc3f77ca7783a1/schema/spacewalk/oracle/procs/lookup_cve.sql
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

CREATE OR REPLACE FUNCTION
LOOKUP_CVE(name_in IN VARCHAR)
RETURNS NUMERIC
AS $$
DECLARE
        name_id         NUMERIC;
BEGIN
        SELECT id
          INTO name_id
          FROM rhnCve
         WHERE name = name_in;
		
        IF NOT FOUND THEN
		            INSERT INTO rhnCve (id, name) VALUES (nextval('rhn_cve_id_seq'), name_in);
		            name_id := currval('rhn_cve_id_seq');

        END IF;

        RETURN name_id;
END; $$ language plpgsql;

