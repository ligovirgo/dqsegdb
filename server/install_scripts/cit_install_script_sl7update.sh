#!/bin/bash

# This is a script to set up one of the data quality segments database (DQsegDB) machines.
# Warning: This script assumes that it is being run by user root.  Installation by any other user will likely produce errors.
# To both view and save the script's output, run it with somehting like:
#   " ./cit_install_script_sl7update.sh  2>&1  |  tee -a  installation_output_$(date +%Y.%m.%d-%H.%M.%S).txt "
# Sometimes the installation script crashes or gets interrupted.  In that case, we don't always want to re-run everything
#   from the start, but it can be awkward to try to run just part of it by hand or insert "if [ 0 -eq 1 ]; then [...] fi"
#   blocks, to skip completed code.  So the script is broken up into blocks, which can be turned on and off independently.
#   Simply set the blocks you want to run to 1 and the blocks that you don't want to run to 0, then re-run the script.
# Here are the different sections and flags that control whether each is run:
run_block_0=1   # * setup variables, used in other sections 
run_block_1=1   # * basic installation items   #basic
run_block_2=1   # * Apache, MariaDB, etc., installation
run_block_3=1   # * configuration of Apache, DB, etc.
run_block_4=1   # * Importing certificates and starting Apache
run_block_5=1   # * Installing segments publisher code
run_block_6=1   # * Handling remaining machine-specific items
run_block_7=1   # * restoring main DQSegDB DB
run_block_8=1   # * Handling crontabs, misc. links
run_block_9=1   # * Unspecified additional commands (probably added by hand at run time)


if [ $run_block_0 -eq 1 ]; then   # * setup variables, used in other sections 
  # set host; valid options: segments, segments-backup, segments-web, segments-dev, segments-dev2, segments-s6, segments-other
  host="segments-backup"   # use this to set the hostname manually
  #host=$(uname -n)   # use this to set the hostname automatically
  if [ $host != "segments" ] && [ $host != "segments-backup" ] && [ $host != "segments-web" ] && [ $host != "segments-dev" ] \
      && [ $host != "segments-dev2" ] && [ $host != "segments-s6" ] && [ $host != "segments-other" ]
  then
    echo "### ERROR ### Variable 'host' is not set to a valid value.  Please fix this and run this script again."
    exit
  fi
  if [ "$host" != `uname -n` ]
  then
    echo "### WARNING ### Hostname is `uname -n`, but 'host' variable is set to $host."
    echo "            ### If this is a mistake, you have 10 seconds to stop this script; after that, installation will continue anyway."
    sleep 10
  fi
  if [ `id -un` != "root" ]
  then
    echo "### WARNING ### User should be 'root' but is actually '`id -un`'.  This script will probably not run correctly."
    echo "            ### You have 10 seconds to stop this script; after that, installation will continue anyway."
    sleep 10
  fi

  # The default is to create a 'live' system, with all services, cron jobs, etc. ready to run immediately;
  #    if you don't want that, change the 'live' variable to 0 before running this script.
  # If 'live' is not 1, some services will be started, as part of setting them up, then shut down after that.
  # NOTE: This doesn't apply to mariadb and httpd yet.
  #       They will be started, no matter what.  We'll work on making that optional later.
  live=1

  # This variable set to 1 will output some messages to the screen and log file (or not, if set to 0).
  # These msgs give some useful information, but also report checkpoints along the installation route (in case of trouble).
  verbose=1

  if [ $verbose -eq 1 ]; then \
    echo -e "### Starting installation: $(date)  \n### hostname: $host"; fi
fi   # run_block_0

if [ $run_block_1 -eq 1 ]; then   # * basic installation items   #basic
  if [ $verbose -eq 1 ]; then echo -e "### Starting basic installation items"; fi   #basic
  # first, make sure that we can get to the installation directories that we need
  if [ ! -d /backup/segdb/reference/install_support/ ]
  then
    echo "### ERROR ### The backup dir with installation files ( /backup/segdb/reference/install_support/ ) is not available."
    echo "          ### Installation cannot be completed properly without the files in that dir.  Exiting."
    exit
  fi
  # make backups of user root config files (if they exist) and then import new files
  cd /root/ 
  if [ -e ./.bashrc ]; then cp  ./.bashrc  ./.bashrc_$(date +%Y.%m.%d-%H.%M.%S).bak ; fi
  if [ -e ./.vimrc ]; then cp  ./.vimrc  ./.vimrc_$(date +%Y.%m.%d-%H.%M.%S).bak ; fi
  if [ -e ./.pythonrc ]; then cp  ./.pythonrc  ./.pythonrc_$(date +%Y.%m.%d-%H.%M.%S).bak ; fi
  #rsync -avP /backup/segdb/segments/install_support/.bashrc .
  #rsync -avP /backup/segdb/segments/install_support/.vimrc .
  #rsync -avP /backup/segdb/segments/install_support/.pythonrc .
  rsync -avP /backup/segdb/reference/install_support/.bashrc .
  rsync -avP /backup/segdb/reference/install_support/.vimrc .
  rsync -avP /backup/segdb/reference/install_support/.pythonrc .
  chown  root:root  .bashrc  .pythonrc  .vimrc
  .  ./.bashrc
  mkdir /root/bin/

  yum -y install git nano mlocate screen telnet   ### install python3?
  mkdir /root/dqsegdb_git
  cd /root/dqsegdb_git
  git clone https://github.com/ligovirgo/dqsegdb.git  
  cd ./dqsegdb/server/install_scripts
  if [ $verbose -eq 1 ]
  then
    echo "### INFO ### Printing the installation script/instructions;  $(date)"
    echo "##########################################################"
    cat cit_install_script_sl7update.sh
    echo "### INFO ### Finished printing the installation script/instructions"
    echo "###################################################################"
  fi

  # used for connecting to git repositories with Kerberos (if this is still used)
  yum -y install ecp-cookie-init
  git config --global http.cookiefile /tmp/ecpcookie.u`id -u`
  #git config --global user.email ryan.fisher@ligo.org
  #git config --global user.name "Ryan Fisher"
  git config --global user.email robert.bruntz@ligo.org
  git config --global user.name "Robert Bruntz"
  # these lines above might be changed to a different user later

  # Set LGMM (LIGO Grid-Mapfile Manager) to run on reboot and start it now
  touch /etc/grid-security/whitelist   ### just in case the config file looks for it; missing an expected file crashes lgmm
  touch /etc/grid-security/blacklist   ### just in case the config file looks for it; missing an expected file crashes lgmm
  cp  /backup/segdb/reference/lgmm/whitelist  /etc/grid-security/
  cp  /etc/lgmm/lgmm_config.py  /etc/lgmm/lgmm_config.py_$(date +%Y.%m.%d-%H.%M.%S).bak
  cp /backup/segdb/reference/install_support/lgmm_config.py  /etc/lgmm/
  touch /etc/grid-security/grid-mapfile
  chown nobody:nobody /etc/grid-security/grid-mapfile
  chmod 644 /etc/grid-security/grid-mapfile
  ### not sure if the order is right for the next 3 lines; 'lgmm -f' seems to need to be run or the service won't stay on
  lgmm -f
  /sbin/chkconfig lgmm on
  systemctl restart lgmm
fi   # run_block_1


if [ $run_block_2 -eq 1 ]; then   # * Apache, MariaDB, etc., installation
  if [ $verbose -eq 1 ]; then echo "### Starting Apache, MariaDB, etc., installation;  $(date)"; fi
  # Install Apache, MariaDB (successor to MySQL), PHPMyAdmin, etc.
  # Install Apache server.
  yum -y install httpd

  # Install Apache WSGI module.
  yum -y install mod_wsgi

  # Install MariaDB, set it to run on startup, and start it
  yum -y install mariadb-server mariadb mariadb-devel
  ### not started until later - b/c we want to change the buffer pool size first?

  # Install PHP (for web interface).
  yum -y install php php-mysql

  yum -y install mod_ssl

  # Install pyodbc library for Python. N.B. This also installs unixODBC as a dependency.
  yum -y install pyodbc

  # By default, unixODBC only installs PostGreSQL connector libraries. Install the MySQL connectors now.
  yum -y install mysql-connector-odbc

  # Increase innodb buffer pool size.
  echo "[mysqld]" >> /etc/my.cnf
  # set max_connections to 256 here? - do in /etc/my.cnf ?
  if [ $host == "segments-dev2" ]
  then
    echo "innodb_buffer_pool_size = 20G" >> /etc/my.cnf
  else
    echo "innodb_buffer_pool_size = 40G" >> /etc/my.cnf
  fi
  ### Note: 20 GB for segments-dev2 is b/c it has limited disk space; others should be fine.  
  ###   (Maybe increase it for some/all others?)

  #if [ $live -eq 1 ]
  #then
  #  systemctl enable mariadb.service
  #  systemctl restart mariadb.service
  #else
  #  echo "### NOTICE ### The 'live' variable is not set to 1, so the mariadb service is not being started."
  #fi
  systemctl enable mariadb.service
  systemctl restart mariadb.service

  # Set up DQSegDB stuff
  # Make DQSEGDB server directories
  mkdir -p /opt/dqsegdb/python_server/logs
  # maybe at some point change the above to /opt/dqsegdb/logs/python_server/, and change python code to match 
  #  (or create a symlink), so that the code and logs are separate?
  chmod 777 /opt/dqsegdb/python_server/logs
  mkdir -p /opt/dqsegdb/python_server/src

  # Add server files.
  cd ~
  git clone https://github.com/ligovirgo/dqsegdb.git
  cp  ~/dqsegdb/server/src/*  /opt/dqsegdb/python_server/src/

  # Add WSGI script alias to Apache configuration file.
  #echo "WSGIScriptAlias / /opt/dqsegdb/python_server/src/application.py" >> /etc/httpd/conf.d/wsgi.conf
  ### why is this done a few lines before the /etc/httpd/conf.d/ dir is moved and replaced???
  ### turns out that the file copied over later (/etc/httpd/conf.d/wsgi.conf) already has this line
  ### so the above line isn't needed at all; it just creates the file, which is then moved


  ## FIX!!! Replace with openssl!!!
  # Install M2Crypto library.
  yum -y install m2crypto
  ### some code uses m2crypto; need to change that code at the same time as (or before) changing this over to openssl

  # Setup ODBC Data Source Name (DSN)
  if [ $host == "segments" ] || [ $host == "segments-web" ] || [ $host == "segments-backup" ] ||  \
     [ $host == "segments-dev" ] || [ $host == "segments-dev2" ]
  then
    if [ -e /etc/odbc.ini ]; then mv  /etc/odbc.ini  /etc/odbc.ini_$(date +%Y.%m.%d-%H.%M.%S).bak ; fi
    cp  /backup/segdb/reference/root_files/$host/odbc.ini  /etc/
  fi

  # Install phpMyAdmin
  ### do we want to do this for every segments machine?
  if [ $host == "segments" ] || [ $host == "segments-web" ] || [ $host == "segments-backup" ] ||  \
     [ $host == "segments-dev" ] || [ $host == "segments-dev2" ]
  then
    yum -y install phpmyadmin
    mv /etc/phpMyAdmin/config.inc.php   /etc/phpMyAdmin/config.inc.php_$(date +%Y.%m.%d-%H.%M.%S).bak
    cp /backup/segdb/reference/install_support/config.inc.php   /etc/phpMyAdmin/
    chown root:apache /etc/phpMyAdmin/config.inc.php
  fi
fi   # run_block_2


if [ $run_block_3 -eq 1 ]; then   # * configuration of Apache, DB, etc.
  if [ $verbose -eq 1 ]; then echo "### Starting configuration of Apache, DB, etc.;  $(date)"; fi
  # Configure application Apache:
  # See 2019.02.12 work notes for comparisons of SL 6 and SL 7 versions of each file
  mv /etc/httpd/conf     /etc/httpd/conf_bak_$(date +%Y.%m.%d-%H.%M.%S)
  mv /etc/httpd/conf.d   /etc/httpd/conf.d_bak_$(date +%Y.%m.%d-%H.%M.%S)
  mkdir /etc/httpd/conf
  mkdir /etc/httpd/conf.d
  cp  /backup/segdb/reference/install_support/segments/etc_httpd_conf_httpd.conf         /etc/httpd/conf/httpd.conf
  cp  /backup/segdb/reference/install_support/segments/etc_httpd_conf_magic              /etc/httpd/conf/magic
  cp  /backup/segdb/reference/install_support/segments/etc_httpd_conf.d_autoindex.conf   /etc/httpd/conf.d/autoindex.conf
  cp  /backup/segdb/reference/install_support/segments/etc_httpd_conf.d_php.conf         /etc/httpd/conf.d/php.conf
  cp  /backup/segdb/reference/install_support/segments/etc_httpd_conf.d_phpMyAdmin.conf  /etc/httpd/conf.d/phpMyAdmin.conf
  cp  /backup/segdb/reference/install_support/segments/etc_httpd_conf.d_ssl.conf         /etc/httpd/conf.d/ssl.conf
  cp  /backup/segdb/reference/install_support/segments/etc_httpd_conf.d_userdir.conf     /etc/httpd/conf.d/userdir.conf
  cp  /backup/segdb/reference/install_support/segments/etc_httpd_conf.d_welcome.conf     /etc/httpd/conf.d/welcome.conf
  cp  /backup/segdb/reference/install_support/segments/etc_httpd_conf.d_wsgi.conf        /etc/httpd/conf.d/wsgi.conf
  cp  /backup/segdb/reference/install_support/segments/etc_httpd_conf.d_README           /etc/httpd/conf.d/README
  # not sure if the file copied in the following line even does anything:
  #cp /backup/segdb/reference/install_support/segments/etc_httpd_conf.d_config.inc.php    /etc/httpd/conf.d/config.inc.php 
  #   segments.ligo.org has both /etc/phpMyAdmin/config.inc.php and /etc/httpd/conf.d/config.inc.php, and it works fine;
  #   segments-dev2.ligo.org has only /etc/phpMyAdmin/config.inc.php, and it works fine;
  #   leaving that line out for now (but the file it would copy is still there)
  if [ $host == "segments" ]
  then   # only segments uses /var/www/nagios/, so only segments gets dqsegdb.conf with that uncommented
    cp /backup/segdb/reference/install_support/segments/etc_httpd_conf.d_dqsegdb.conf      /etc/httpd/conf.d/dqsegdb.conf
  else
    cp /backup/segdb/reference/install_support/segments-dev/etc_httpd_conf.d_dqsegdb.conf  /etc/httpd/conf.d/dqsegdb.conf
  fi
  if [ $host == "segments-web" ]
  then
    # we'll do all of the Shibboleth stuff here, in one go, rather than splitting it up
    cd /etc/yum.repos.d/ 
    wget http://download.opensuse.org/repositories/security:/shibboleth/CentOS_7/security:shibboleth.repo
    yum -y install shibboleth   # I think this creates /etc/httpd/conf.d/shib.conf, which will then be backed up
    # yum install -y ligo-shibboleth-sp   # I think this was the old installation package
    mv /etc/httpd/conf.d/shib.conf  /etc/httpd/conf.d/shib.conf_$(date +%Y.%m.%d-%H.%M.%S).bak
    mv /etc/httpd/conf.d/dqsegdb.conf /etc/httpd/conf.d/dqsegdb.conf_other_machines
    cp -p  /backup/segdb/reference/install_support/segments-web/etc_httpd_conf.d_dqsegdb.conf  /etc/httpd/conf.d/dqsegdb.conf
    cp -p  /backup/segdb/reference/install_support/segments-web/etc_httpd_conf.d_shib.conf     /etc/httpd/conf.d/shib.conf
    cp -rp /backup/segdb/reference/install_support/segments-web/shib_self_cert                 /root/
    chmod 0600 /root/shib_self_cert/selfsignedkey.pem
    chmod 0644 /root/shib_self_cert/selfsignedcert.pem
 # which of the following do we need to do?
    cp -p /root/shib_self_cert/selfsignedcert.pem          /etc/shibboleth/sp-cert.pem
    cp -p /root/shib_self_cert/selfsignedcert.pem          /etc/shibboleth/sp-signing-cert.pem
    cp -p /root/shib_self_cert/selfsignedkey.pem           /etc/shibboleth/sp-key.pem
    cp -p /root/shib_self_cert/selfsignedkey.pem           /etc/shibboleth/sp-signing-key.pem
    chown shibd:shibd /etc/shibboleth/sp*cert.pem   # do we need to do this?
    chown shibd:shibd /etc/shibboleth/sp*key.pem
    cd /etc/shibboleth
    wget https://wiki.ligo.org/pub/AuthProject/DeployLIGOShibbolethSL7/login.ligo.org.cert.LIGOCA.pem
    wget https://wiki.ligo.org/pub/AuthProject/DeployLIGOShibbolethSL7/shibboleth2.xml
    wget https://wiki.ligo.org/pub/AuthProject/DeployLIGOShibbolethSL7/attribute-map.xml
    # the above are the main way to get those 3 files; below are a secondary option (which might not be equivalent)
    #cp -p /backup/segdb/reference/install_support/segments-web/login.ligo.org.cert.LIGOCA.pem
    #cp -p /etc/shibboleth/attribute-map-ligo.xml           /etc/shibboleth/attribute-map.xml
    #cp -p /etc/shibboleth/shibboleth2-ligo-template01.xml  /etc/shibboleth/shibboleth2.xml
    #sed -i 's/YOUR_ENTITY_ID/https\:\/\/segments-web.ligo.org\/shibboleth-sp/g'  /etc/shibboleth/shibboleth2.xml
    # the following line replaces 'entityID=""' with 'entityID="https://login.ligo.org/idp/shibboleth"'
    sed -i 's/entityID\=\"\"/entityID\=\"https\:\/\/segments-web.ligo.org\/shibboleth-sp\"/g'  /etc/shibboleth/shibboleth2.xml
    # the following probably duplicates (and adds to) a section within shib.conf, but that's *probably* OK
    echo "<Location /secure>"  >>  /etc/httpd/conf.d/shib.conf
    echo " AuthType shibboleth"  >>  /etc/httpd/conf.d/shib.conf
    echo " ShibRequestSetting requireSession 1"  >>  /etc/httpd/conf.d/shib.conf
    echo " <RequireAll>"  >>  /etc/httpd/conf.d/shib.conf
    echo " require shib-session"  >>  /etc/httpd/conf.d/shib.conf
    echo " require shib-attr isMemberOf Communities:LSCVirgoLIGOGroupMembers"  >>  /etc/httpd/conf.d/shib.conf
    echo " </RequireAll>"  >>  /etc/httpd/conf.d/shib.conf
    echo "</Location>"  >>  /etc/httpd/conf.d/shib.conf
    cp -p  /backup/segdb/reference/install_support/segments-web/lsc-logo.jpg  /etc/shibboleth/
  fi
  chown -R root:root /etc/httpd/conf.d
  chown -R root:root /etc/httpd/conf

  # Get the 2 IP addresses (internal network and external network) and the hostname
  # issue: on different systems, eth0 = eno1 = ens10 (10.14.xx.xx address); eth1 = eno2 = ens3 (131.215.xx.xx address)
  # not all installations can use the following lines; the "grep "inet 10""-type lines work on SL 7.5, but not 6.1 
  # on SL7, the line looks like "inet 10.14.0.106  netmask 255.255.0.0  broadcast 10.14.255.255"
  int_addr=`ifconfig | grep "inet 10" | awk '{print $2}'`
  #int_addr=`ifconfig ens10 | grep "inet " | awk '{print $2}'`
  #int_addr=`ifconfig ens10 |sed -n 's/.*inet \([0-9\.]*\).*/\1/p'`
  #int_addr=`ifconfig eno1 |sed -n 's/.*inet addr:\([0-9\.]*\).*/\1/p'`
  # on SL7, the line looks like "inet 131.215.113.159  netmask 255.255.255.0  broadcast 131.215.113.255"
  ext_addr=`ifconfig | grep "inet 131" | awk '{print $2}'`
  #ext_addr=`ifconfig ens3 | grep "inet " | awk '{print $2}'`
  #ext_addr=`ifconfig ens3 |sed -n 's/.*inet \([0-9\.]*\).*/\1/p'`
  #ext_addr=`ifconfig eno2 |sed -n 's/.*inet addr:\([0-9\.]*\).*/\1/p'` 
  echo "internal network address =  $int_addr"
  echo "external network address =  $ext_addr"
  server_name=`hostname -f`
  echo "server name =  $server_name"

  # Replace the IP addresses and hostname in the dqsegdb config file (which has values for segments.ligo.org by default)
  cp /etc/httpd/conf.d/dqsegdb.conf /etc/httpd/conf.d/dqsegdb.conf_$(date +%Y.%m.%d-%H.%M.%S).bak
    sed -i "s/segments\.ligo\.org/${server_name}/g"   /etc/httpd/conf.d/dqsegdb.conf
    sed -i "s/131\.215\.113\.156/${ext_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
    sed -i "s/10\.14\.0\.101/${int_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf

  echo "OPENSSL_ALLOW_PROXY_CERTS=1" >> /etc/sysconfig/httpd 
  echo 'PYTHONPATH="/opt/dqsegdb/python_server/src:${PYTHONPATH}"'>> /etc/sysconfig/httpd 

  # Import data and create main database.
  ### this is now done at the very end of the script, b/c it takes so long to restore the full dqsegdb
 
  # Create database users and give them privileges
  ### Note that the ‘empty_database.tgz’ and dqsegdb backups have users ‘dqsegdb_user’ and ‘admin’, 
  ###      but they don’t work right, so we create the users and give them permissions even before the DB is restored
  ### old way of doing it here:
  #cp  /backup/segdb/reference/install_support/mysql_user_commands.sh  /root/bin/
  #/bin/bash  /root/bin/mysql_user_commands.sh
  #rm  /root/bin/mysql_user_commands.sh
  ### new way of doing it here:
  if [ $host != "" ]; then mysql -uroot -A < /backup/segdb/reference/install_support/${host}/MySQLUserGrants.sql; fi

  ### Restore an *empty* dqsegdb here
  ### Note that this will have tables, flags, etc., incl. users ‘dqsegdb_user’ and ‘admin’
  if [ 1 -eq 0 ]; then
    ### this part is to restore a *blank* DB, not a backed-up DB
    ### this part isn't currently an option; the code is parked here in case we ever want to make it an option
    mkdir /root/empty_database
    cp /backup/segdb/reference/install_support/empty_database.tgz  /root/empty_database/
    cp /backup/segdb/reference/install_support/segments/populate_from_backup.sh  /root/empty_database/
    cd /root/empty_database/
    tar xvzf empty_database.tgz
    #/bin/bash ./populate_from_backup.sh
    sudo -u ldbd ./populate_from_backup.sh
  fi
fi   # run_block_3


if [ $run_block_4 -eq 1 ]; then   # * Importing certificates and starting Apache
  if [ $verbose -eq 1 ]; then echo "### Importing certificates and starting Apache;  $(date)"; fi
  # move certs to appropriate locations, as referenced by /etc/httpd/conf.d/dqsegdb.conf
  if [ $host == "segments" ]; then \
    cp  /backup/segdb/reference/install_support/segments/ldbd*pem  /etc/grid-security/; \
    cp  /backup/segdb/reference/install_support/segments/robot*pem  /etc/grid-security/; \
    cp  /backup/segdb/reference/install_support/segments/segments.ligo.org.*  /etc/grid-security/; \
    # what uses the files in this next dir? can we skip it?
    if [ ! -d /etc/httpd/x509-certs/ ]; then mkdir -p /etc/httpd/x509-certs/; fi; \
    cp  /backup/segdb/reference/install_support/segments/segments.ligo.org.*  /etc/httpd/x509-certs/; fi
  if [ $host == "segments-backup" ]; then \
    cp  /backup/segdb/reference/install_support/segments/robot*pem  /etc/grid-security/; \
    cp  /backup/segdb/reference/install_support/segments-backup/segments-backup.ligo.org.*  /etc/grid-security/; fi
  if [ $host == "segments-web" ]; then \
    cp  /backup/segdb/reference/install_support/segments-web/segments-web.ligo.org.*  /etc/grid-security/; \
    # what uses the files in this next dir? can we skip it?
    if [ ! -d /etc/httpd/x509-certs/ ]; then mkdir -p /etc/httpd/x509-certs/; fi; \
    cp  /backup/segdb/reference/install_support/segments-web/segments-web.ligo.org.*  /etc/httpd/x509-certs/; fi
  if [ $host == "segments-dev" ]; then \
    cp  /backup/segdb/reference/install_support/segments-dev/ldbd*pem  /etc/grid-security/; \
    cp  /backup/segdb/reference/install_support/segments-dev/robot*pem  /etc/grid-security/; \
    cp  /backup/segdb/reference/install_support/segments-dev/segments-dev.ligo.org.*  /etc/grid-security/; fi
  if [ $host == "segments-dev2" ]; then \
  #   cp  /backup/segdb/reference/install_support/segments-dev/ldbd*pem  /etc/grid-security/; \   ### do we need this?
    cp  /backup/segdb/reference/install_support/segments-dev2/segments-dev2.ligo.org.*  /etc/grid-security/; fi
  if [ $host == "segments-s6" ]; then \
    cp  /backup/segdb/reference/install_support/segments-s6/segments-s6.ligo.org.*  /etc/grid-security/; fi
  cp /etc/pki/tls/certs/localhost.crt /etc/pki/tls/certs/localhost.crt_$(date +%Y.%m.%d-%H.%M.%S).bak
  cp /etc/pki/tls/private/localhost.key /etc/pki/tls/private/localhost.key_$(date +%Y.%m.%d-%H.%M.%S).bak
  cp /etc/grid-security/${host}.ligo.org.pem /etc/pki/tls/certs/localhost.crt 
  cp /etc/grid-security/${host}.ligo.org.key /etc/pki/tls/private/localhost.key

  # Get all cert identifier packages:
  yum -y install cilogon-ca-certs
  ### the above package is no longer available; do we need it (I.e., its replacement) anymore?
  yum -y install osg-ca-certs
  yum -y install ligo-ca-certs

  # Start Apache server.
  systemctl enable httpd.service
  #chkconfig httpd on   ### old version
  systemctl restart httpd.service
  #/etc/init.d/httpd restart   ### old version

  # Add Web Interface configuration.
  ### which machine(s) use(s) this? create a targeted if-then block for that/those machine(s)
  ### this was probably from the old segments.ligo.org/web (or whatever it was called) interface)
  ### nothing should need this anymore; kept it for reference, just in case
  #echo "Alias /dqsegdb_web /usr/share/dqsegdb_web" >> /etc/httpd/conf.d/dqsegdb_web.conf

  # more stuff
  yum -y install glue lal lal-python python-pyRXP
fi   # run_block_4


if [ $run_block_5 -eq 1 ]; then   # * Installing segments publisher code   ### Publishing   #publishing
  if [ $host == "segments" ] || [ $host == "segments-dev" ] || [ $host == "segments-backup" ]; then
    if [ $verbose -eq 1 ]; then echo "### Installing publisher code;  $(date)"; fi
    mkdir -p /dqxml/H1
    mkdir -p /dqxml/L1
    mkdir -p /dqxml/V1
    mkdir -p /dqxml/G1
    chown dqxml:dqxml  /dqxml/H1
    chown dqxml:dqxml  /dqxml/L1
    #cp  /backup/segdb/reference/install_support/etc_init.d_dir/dqxml_pull_from_obs  /etc/init.d/
    #cp  /backup/segdb/reference/install_support/root_bin_dir/dqxml_pull_from_obs  /root/bin/
    # note that the manual rsyncs scripts for LHO and LLO are just there for backup, not regular use
    cp  /backup/segdb/reference/install_support/segments/root_bin/manual_rsync_GEO.sh  /root/bin/
    cp  /backup/segdb/reference/install_support/segments/root_bin/manual_rsync_LHO.sh  /root/bin/
    cp  /backup/segdb/reference/install_support/segments/root_bin/manual_rsync_LLO.sh  /root/bin/
    cp  /backup/segdb/reference/install_support/segments/root_bin/manual_rsync_VGO.sh  /root/bin/
    cp  /backup/segdb/reference/install_support/ligolw_dtd.txt  /root/bin/
    cp  /backup/segdb/reference/install_support/dqsegdb_September_11_2018.tgz  /root/
    ### should we be installing this from github, rather than a static file?
  cd /root/
  tar xzf dqsegdb_September_11_2018.tgz
  # 'glue' fix to publisher code; we should incorporate this into the code on github and use that at some point
    mv  /root/dqsegdb_September_11_2018/dqsegdb/bin/ligolw_publish_threaded_dqxml_dqsegdb  \
        /root/dqsegdb_September_11_2018/dqsegdb/bin/ligolw_publish_threaded_dqxml_dqsegdb_2019.03.05.bak
    cp /backup/segdb/reference/install_support/ligolw_publish_threaded_dqxml_dqsegdb_2019.03.05_fix  \
       /root/dqsegdb_September_11_2018/dqsegdb/bin/
    ln -s /backup/segdb/reference/install_support/ligolw_publish_threaded_dqxml_dqsegdb_2019.03.05_fix  \
          /root/dqsegdb_September_11_2018/dqsegdb/bin/ligolw_publish_threaded_dqxml_dqsegdb
  # here is the actual publisher code
    cp /backup/segdb/reference/install_support/segments/root_bin/run_publishing_O3_segmentsligoorg.sh_new_*    /root/bin/
    cp /backup/segdb/reference/install_support/segments/root_bin/run_publishing_O3_segmentsligoorg_G1_test.sh  /root/bin/
    cd /root/bin/
    ln -s `ls -1rt run_publishing_O3_segmentsligoorg.sh_new_????.??.?? | tail -n 1`  run_publishing_O3_segmentsligoorg.sh
    if [ $host == "segments-dev" ];    then sed -i 's/segments/segments-dev/g'    run_publishing_O3_segmentsligoorg.sh; fi 
    if [ $host == "segments-backup" ]; then sed -i 's/segments/segments-backup/g' run_publishing_O3_segmentsligoorg.sh; fi 
    cp /backup/segdb/reference/install_support/segments/root_bin/fix_3_commas.sh  /dqxml/
    mkdir /root/bad_dqxml/
    if [ $host == "segments" ]
    then
      cp  /backup/segdb/reference/install_support/etc_init.d_dir/dqxml_push_to_ifocache  /etc/init.d/
      cp  /backup/segdb/reference/install_support/root_bin_dir/dqxml_push_to_ifocache  /root/bin/
    fi
    mkdir -p /var/log/publishing/dev/
    mkdir -p /var/log/publishing/state/
    mkdir -p /var/log/publishing/pid/
    if [ 0 -eq 1 ]; then
      ### this wouldn't be done for a regular installation
      cp /backup/segdb/segments-dev/install/blank-DQ_Segments_current_dev.xml  /var/log/publishing/state/
      cp /backup/segdb/segments-dev/install/blank-DQ_Segments_current_dev.xml  /var/log/publishing/state/H-DQ_Segments_current_dev.xml
      cp /backup/segdb/segments-dev/install/blank-DQ_Segments_current_dev.xml  /var/log/publishing/state/L-DQ_Segments_current_dev.xml
      cp /backup/segdb/segments-dev/install/blank-DQ_Segments_current_dev.xml  /var/log/publishing/state/V-DQ_Segments_current_dev.xml
      cp /backup/segdb/segments-dev/install/blank-DQ_Segments_current_dev.xml  /var/log/publishing/state/G-DQ_Segments_current_dev.xml
    fi
    #latest_state_dir=`ls -1tr /backup/segdb/segments/publisher/spool/ | tail -n 1`
    latest_state_dir=`ls -1tr /backup/segdb/segments/publisher/spool/ | tail -n 2 | head -n 1`
      ### would it be better to go back one day for state files, to be safe? then just re-publish that one day's segments? 
      ### if so, replace 'tail -n 1' with 'tail -n 2 | head -n 1'
      ### DB backup is done at 00:00; 'spool_backup' is done at 00:07; that means that ~7 minutes of segments will be
      ###   recorded in the state file, but won't show up in the backup
    cp /backup/segdb/segments/publisher/spool/$latest_state_dir/*  /var/log/publishing/state/

    ### something looks for the ligolw_dtd.txt file here, doesn't it? (check; if not, get rid of this)
    mkdir -p /root/Publisher/etc/
    cp  /backup/segdb/reference/install_support/ligolw_dtd.txt  /root/Publisher/etc/

    cp  /backup/segdb/reference/lgmm/grid-mapfile-insert  /etc/grid-security/

    if [ $live -eq 1 ]
    then
      #/sbin/chkconfig  dqxml_pull_from_obs  on
      #systemctl start dqxml_pull_from_obs.service
      echo 1 > /root/bin/start_manual_rsync_GEO.txt
      echo 1 > /root/bin/start_manual_rsync_VGO.txt
  #    nohup  /root/bin/manual_rsync_GEO.sh  >>  /root/bin/manual_rsync_GEO_log.txt  &
  #    nohup  /root/bin/manual_rsync_VGO.sh  >>  /root/bin/manual_rsync_VGO_log.txt  &
      if [ $host == "segments" ]
      then 
        /sbin/chkconfig  dqxml_push_to_ifocache  on 
        systemctl start dqxml_push_to_ifocache.service
      fi
    fi
    # create some useful links
    ln -s  /root/dqsegdb_September_11_2018   /root/bin/dqsegdb_current_code
    ln -s  /var/log/publishing/pid/          /root/bin/pid_files
    ln -s  /var/log/publishing/dev           /root/bin/publisher_log_files
    ln -s  /var/log/publishing/state/        /root/bin/state_files
  fi
fi   # run_block_5


if [ $run_block_6 -eq 1 ]; then   # * Handling remaining machine-specific items
  if [ $verbose -eq 1 ]; then echo "### Handling remaining machine-specific items;  $(date)"; fi
  if [ $host == "segments" ]
  then
    mkdir -p /usr1/ldbd/
    mkdir -p /usr1/ldbd/bin
    cp -p  /backup/segdb/reference/install_support/segments/ldbd/backup_dqsegdb_mysqldatabase_newdir.sh    /usr1/ldbd/bin/
    cp -p  /backup/segdb/reference/install_support/segments/ldbd/weekly_backup_rotate_newdir.py            /usr1/ldbd/bin/
    cp -p  /backup/segdb/reference/install_support/segments/ldbd/monthly_backup_newdir.py                  /usr1/ldbd/bin/
    cp -p  /backup/segdb/reference/install_support/segments/ldbd/daily_backup_rotate_newdir.py             /usr1/ldbd/bin/
    cp -p  /backup/segdb/reference/install_support/segments/ldbd/log_backup.sh                             /usr1/ldbd/bin/
    cp -p  /backup/segdb/reference/install_support/segments/ldbd/spool_backup.sh                           /usr1/ldbd/bin/
    cp -p  /backup/segdb/reference/install_support/segments/ldbd/backup_opt_dqsegdb_python_server_logs.py  /usr1/ldbd/bin/
    chown -R ldbd:ldbd /usr1/ldbd
  fi
  if [ $host == "segments-backup" ]
  then
    mkdir -p /usr1/ldbd/
    mkdir -p /usr1/ldbd/bin
    mkdir -p /usr1/ldbd/backup_logging
    cp  /backup/segdb/reference/install_support/segments-backup/ldbd/populate_from_backup.sh  /usr1/ldbd/bin/
    cp  /backup/segdb/reference/install_support/segments-backup/ldbd/backup_dqsegdb_regression_tests_mysqldatabase.sh  \
          /usr1/ldbd/bin/
    cp  /backup/segdb/segments/backup_logging/import_time.log  /usr1/ldbd/backup_logging/
    chown -R ldbd:ldbd /usr1/ldbd
    cp  /backup/segdb/reference/install_support/segments-backup/root_bin/run_regression.sh  /root/bin/
  # this part sets up the regression tests themselves
    mkdir -p /opt/dqsegdb/regression_test_suite/
    mkdir -p /opt/dqsegdb/logs/regression_test_suite/
    cp -rp  /root/dqsegdb_git/dqsegdb/server/db/db_utils/component_interface_data_integrity_test_suite/src  \
            /opt/dqsegdb/regression_test_suite/
    # there is an issue with DAO.py and /usr/lib64/python2.7/site-packages/MySQLdb/cursors.py; this fixes it;
    #   see work notes for 2019.02.20 for details and 2019.04.03 for the (wrong) fix and 2019.04.05 for the kludge fix
    cp /opt/dqsegdb/regression_test_suite/src/DAO.py  \
       /opt/dqsegdb/regression_test_suite/src/DAO.py_$(date +%Y.%m.%d-%H.%M.%S).bak
    #sed -i 's/str(dataset_id))/["str(dataset_id)"]/g' /opt/dqsegdb/regression_test_suite/src/DAO.py
    cp /backup/segdb/reference/install_support/segments-backup/DAO.py_2019.02.20_test.py  \
       /opt/dqsegdb/regression_test_suite/src/
    ln -s  /opt/dqsegdb/regression_test_suite/src/DAO.py_2019.02.20_test.py  /opt/dqsegdb/regression_test_suite/src/DAO.py
    yum -y install MySQL-python
  # this part restores a backed-up regression test DB (dqsegdb DB is restored later)
    output_date=`date +%Y.%m.%d-%H.%M.%S`
    tmp_dir=/backup/segdb/segments/install_support/tmp/${host}_restore_${output_date}
    mkdir -p  $tmp_dir
    cp /backup/segdb/reference/install_support/populate_from_backup_dqsegdb_regression_tests_for_installation_script.sh  $tmp_dir
    cp /backup/segdb/segments/regression_tests/dqsegdb_regression_tests_backup.tgz  $tmp_dir
    cd $tmp_dir
    tar xvzf dqsegdb_regression_tests_backup.tgz --no-same-owner   # "--no-same-owner" avoids errors
    sudo -u ldbd ./populate_from_backup_dqsegdb_regression_tests_for_installation_script.sh  $tmp_dir  dqsegdb_regression_tests
    cd /root/
    rm -rf  $tmp_dir
    # create the users and privileges associated with the regression test DB
    mysql -uroot -A < /backup/segdb/reference/install_support/${host}/MySQLUserGrants_tables.sql
  fi
  if [ $host == "segments-web" ]
  then
    systemctl enable shibd.service
    systemctl restart shibd.service
    cp /backup/segdb/reference/install_support/segments-web/lstatus                /root/bin/
    cp /backup/segdb/reference/install_support/segments-web/backup_dqsegdb_web.sh  /root/bin/
    mkdir -p /usr/share/dqsegdb_web
    cp -rp  /root/dqsegdb_git/dqsegdb/web/src/*  /usr/share/dqsegdb_web/
    mv  /usr/share/dqsegdb_web/classes/GetContent.php  /usr/share/dqsegdb_web/classes/GetContent.php_$(date +%Y.%m.%d-%H.%M.%S).bak
    cp -r  /backup/segdb/reference/install_support/segments-web/usr_share_dqsegdb_web_classes_GetContent.php  \
             /usr/share/dqsegdb_web/classes/
    mv  /usr/share/dqsegdb_web/classes/InitVar.php  /usr/share/dqsegdb_web/classes/InitVar.php_$(date +%Y.%m.%d-%H.%M.%S).bak
    cp -r  /backup/segdb/reference/install_support/segments-web/usr_share_dqsegdb_web_classes_InitVar.php  \
             /usr/share/dqsegdb_web/classes/
    mv  /usr/share/dqsegdb_web/classes/JSActions.php  /usr/share/dqsegdb_web/classes/JSActions.php_$(date +%Y.%m.%d-%H.%M.%S).bak
    cp -r  /backup/segdb/reference/install_support/segments-web/usr_share_dqsegdb_web_classes_JSActions.php  \
             /usr/share/dqsegdb_web/classes/
    mv  /usr/share/dqsegdb_web/python_utilities/convert_formats.py  \
        /usr/share/dqsegdb_web/python_utilities/convert_formats.py_$(date +%Y.%m.%d-%H.%M.%S).bak
    cp -r  /backup/segdb/reference/install_support/segments-web/usr_share_dqsegdb_web_python_utilities_convert_formats.py  \
             /usr/share/dqsegdb_web/python_utilities/
    #mkdir /usr/share/dqsegdb_web/downloads
    cd /usr/share/dqsegdb_web/
    tar xzf  /backup/segdb/reference/install_support/segments-web/downloads.tgz   # this will make the dir downloads itself
### ownership and permissions for files in /usr/share/dqsegdb_web ??
  # this part restores a backed-up dqsegdb_web DB (contains info on past segments-web queries)
    backup_dir=/backup/segdb/reference/install_support/segments-web/dqsegdb_web_db/
    /backup/segdb/reference/install_support/populate_from_backup_for_installation_script.sh  $backup_dir  dqsegdb_web
  # create the users and privileges associated with the DB
    mysql -uroot -A < /backup/segdb/reference/install_support/${host}/MySQLUserGrants.sql
  ###segments-web
  # /etc/httpd/
    ### change this to pull files from the server's installation dir, rather than ~~/root_files/[host]/ ?
    cp  `ls -1rt /backup/segdb/reference/root_files/$host/crontab_-l_root* | tail -n 1` /var/spool/cron/root
    # if there's trouble with iptables, these files might help:
    # /backup/segdb/reference/install_support/segments-web/etc_sysconfig_iptables__segments-web_old
    # /backup/segdb/reference/install_support/segments-web/etc_sysconfig_iptables-config__segments-web_old
  fi
  if [ $host == "segments-dev" ]
  then
    # segments-dev doesn't have any dedicated tasks that would need to be filled in here at the moment
    mkdir -p /usr1/ldbd/
    mkdir -p /usr1/ldbd/bin
    chown -R ldbd:ldbd /usr1/ldbd
  fi
  # note: no user 'ldbd' used on segments-web; we aren't planning to ever restore segments-s6; segments-dev2 is done manually
fi   # run_block_6


if [ $run_block_7 -eq 1 ]; then   # * restoring main DQSegDB DB
  if [ $host == "segments" ]  || [ $host == "segments-dev" ] || [ $host == "segments-backup" ]
  then
    if [ $verbose -eq 1 ]; then echo "### Starting restoring main DQSegDB DB;  $(date)"; fi
    # this part restores a backed-up segments DB
    output_date=`date +%Y.%m.%d-%H.%M.%S`
    tmp_dir=/backup/segdb/segments/install_support/tmp/${host}_restore_${output_date}
    mkdir -p  $tmp_dir
    cp /backup/segdb/reference/install_support/populate_from_backup_for_installation_script.sh  $tmp_dir
    cp /backup/segdb/segments/primary/*.tar.gz  $tmp_dir
    cd $tmp_dir
    tar xvzf *.tar.gz --no-same-owner   # "--no-same-owner" flag avoids some errors
    # in the script, first arg is the location of the DB files; second arg is the name of the DB to be restored
    if [ $host == "segments-backup" ]
    then
      # segments-backup has a different name for its DB
      sudo -u ldbd ./populate_from_backup_for_installation_script.sh  $tmp_dir  segments_backup
      # create the users and privileges associated with specific tables, after DB exists (only necessary on segments-backup)
      mysql -uroot -A < /backup/segdb/reference/install_support/${host}/MySQLUserGrants_tables.sql
    else
      sudo -u ldbd ./populate_from_backup_for_installation_script.sh  $tmp_dir  dqsegdb
    fi
    cd ~
    rm -rf  $tmp_dir
  fi
fi   # run_block_7


if [ $run_block_8 -eq 1 ]; then   # * Handling crontabs, misc. links
  if [ $verbose -eq 1 ]; then echo "### Handling crontabs, misc. links;  $(date)"; fi
  # create crontab files; note that this must happen after the DBs are restored, since some cron jobs will write/publish to DBs
  # first, backup any existing cron files that would be overwritten (though there shouldn't be any)
  if [ -e /var/spool/cron/root ]; then cp /var/spool/cron/root /root/cron_root_bak_$(date +%Y.%m.%d-%H.%M.%S) ; fi
  if [ -e /var/spool/cron/ldbd ]; then cp /var/spool/cron/ldbd /root/cron_ldbd_bak_$(date +%Y.%m.%d-%H.%M.%S) ; fi
  if [ $host == "segments" ] || [ $host == "segments-dev" ] || [ $host == "segments-backup" ]
  then
    if [ $live -eq 1 ]; then
      ### change this to pull files from the server's installation dir, rather than ~~/root_files/[host]/ ?
      cp  `ls -1rt /backup/segdb/reference/root_files/$host/crontab_-l_root* | tail -n 1` /var/spool/cron/root
      cp  `ls -1rt /backup/segdb/reference/ldbd_files/$host/crontab_-l_ldbd* | tail -n 1` /var/spool/cron/ldbd
    else
      cp  `ls -1rt /backup/segdb/reference/root_files/$host/crontab_-l_root*all_lines_commented* | tail -n 1` /var/spool/cron/root
      cp  `ls -1rt /backup/segdb/reference/ldbd_files/$host/crontab_-l_ldbd*all_lines_commented* | tail -n 1` /var/spool/cron/ldbd
    fi
    # create dir to hold files that are created by a cron job, then grabbed by Nagios, for use on monitor.ligo.org:
    if [ $host == "segments" ]
    then
      if [ ! -d /var/www/nagios/ ]; then mkdir -p /var/www/nagios/ ; fi
      ### these first lines fix the glue issue from March 2019; need to fix the original code, instead
      cp /backup/segdb/reference/install_support/segments/root_bin/check_pending_files_2019.03.05.bak  /root/bin/
      cp /backup/segdb/reference/install_support/segments/root_bin/check_pending_files_2019.03.05.fix  /root/bin/
      ln -sf  /root/bin/check_pending_files_2019.03.05.fix  /root/bin/check_pending_files
      cp /backup/segdb/reference/install_support/segments/root_bin/check_pending_files_wrapper_H.sh    /root/bin/
      cp /backup/segdb/reference/install_support/segments/root_bin/check_pending_files_wrapper_L.sh    /root/bin/
      cp /backup/segdb/reference/install_support/segments/root_bin/check_pending_files_wrapper_V.sh    /root/bin/
    fi
  fi
  # Note that there are currently (May 2019) no crontabs for any users on segments-dev2, 
  #   and segments-s6 is likely to be decommissioned very soon, so it does not need to be handled.

  cp  /backup/segdb/reference/root_files/${host}/bin/lstatus*  /root/bin/

  # create some useful links for every machine
  # format reminder: 'ln -s [actual_file]   [link_name]'
  ln -s  /var/log/httpd/                   /root/bin/httpd_logs
  ln -s  /opt/dqsegdb/python_server/logs/  /root/bin/python_server_log_files
fi   # run_block_8


if [ $run_block_9 -eq 1 ]; then   # * Unspecified additional commands (probably added by hand at run time)
  sleep 0   # have to do *something* or Bash gets cranky
fi   # run_block_9

### User tasks to be performed manually:
#  * on segments-backup: run these commands as root, if you want to start pulling DQ XML files from GEO and Virgo:
#      nohup  /root/bin/manual_rsync_GEO.sh  >>  /root/bin/manual_rsync_GEO_log.txt  &
#      nohup  /root/bin/manual_rsync_VGO.sh  >>  /root/bin/manual_rsync_VGO_log.txt  &

if [ $verbose -eq 1 ]; then echo -e "### Finished installation:  $(date)"; fi

exit


### to do:
### * do ownership and permissions for files in /usr/share/dqsegdb_web matter??
### * make sure duplicate section in shib.conf won't be an issue (added by the multiple echo >> shib.conf lines)
### * what is/are ldbd*pem used for? does segments-backup now need that? what about /etc/httpd/x509-certs/?
### * which shib certificate names do we use?
### * verify that the shib installation instructions work
### * install python3?
### * should we increase the "innodb buffer pool size" for non-dev2 systems?
### * question about "set max_connections to 256 here? - do in /etc/my.cnf ?"
### * modify and use code on github, rather than copying 'dqsegdb_September_11_2018.tgz' over and using that
### * incorporate 'glue' fix to publisher code into github code; use that, rather than the patch here
### * fix the 'state files saved after backup' issue
### * where does the 'check_pending_files' script live? fix it there and use that, rather than doing the glue fix here
### * come up with an actual fix for the DAO.py issue; implement it here
### * does anything use /root/Publisher/etc/ligolw_dtd.txt ? if not, get rid of it
### * should "/dqxml/V1" and "/dqxml/G1" also be owned by user dqxml? (change code on the publisher machine, too)
### * do segments and segments-web actually need /etc/httpd/x509-certs/?
### * can we get rid of the "cilogon-ca-certs" line? (or should we replace it?)
### * figure out /etc/phpMyAdmin/config.inc.php vs. /etc/httpd/conf.d/config.inc.php - just diff. loc's. for same file?
### * do we still need the "connecting to git repositories with Kerberos" part?
### * figure out the m2crypto/"Replace with openssl" part - what do we need to do? can we do it?
### * 
### * expand what the "live" variable controls (to include everything that it should control)
### *   this includes: MariaDB, ...?
### * 



