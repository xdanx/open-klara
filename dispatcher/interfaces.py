import logging
import config
import smtplib
import json
import pymysql
from email.mime.text import MIMEText


class mysql():

    def __init__(self, connection):
        # This is how we infer the connection
        self.connection = connection

    # Returns the location of the agent or None of query failed
    # Main Handler will write a log of this
    def authorize_agent(self, auth):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # or the query returnes more than 1 row
            query = "SELECT id FROM agents WHERE auth = %s"
            cursor.execute(query, auth)
            result = cursor.fetchone()

            # If we didn't get exactly 1 answer, there is a problem
            if result is None:
                return None
            if len(result) == 0:
                return None
            elif len(result) == 1:
                return result['id']
            else:
                # TODO: LOG THIS problem. More than 2 results fetched
                return None

    # For all available jobs return their {id:x, 'fileset_scan'}
    # in a json list
    def fetch_available_jobs(self):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = "SELECT id, description FROM jobs WHERE `status` = 'new'"
            cursor.execute(query)
            result = cursor.fetchall()
            our_answer = list()
            for entry in result:
                try:
                    entry_description = json.loads(entry['description'])
                    if 'fileset_scan' in entry_description:
                        # If fileset scan is indeed in our description, we add
                        # this entry in our answer
                        our_answer.append({
                            'id': entry['id'],
                            'fileset_scan': entry_description['fileset_scan']
                        })
                except Exception:
                    continue
            return json.dumps(our_answer)

    # Assigns the job id to the agent id.
    # Returns as status 'assigned' or 'rejected'
    def assign_new_job(self, agent_id, job_id):

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        # One final check + lock the row
        # Start transaction
        cursor.execute("BEGIN")
        self.connection.commit()
        # Let's see if the current job has been assigned meanwhile
        # We use SELECT FOR UPDATE to lock the entire row!
        query = "SELECT id, status, rules FROM jobs WHERE `id` = %s FOR UPDATE"
        cursor.execute(query, job_id)
        result = cursor.fetchone()
        # There will be one answer or 0 for sure, due to index on id
        answer = dict()
        # Check the answer number
        if result is not None:
            # Job still exists!

            if result['status'] != "new":
                # Job has been already assigned!
                answer['status'] = "rejected"
            else:
                # Job is available! Let's fetch it!
                # Marking the job as assigned
                query = "UPDATE jobs \
                        SET `status` = 'assigned', `agent_id` = %s \
                        WHERE `id` = %s"
                cursor.execute(query, (agent_id, job_id))
                self.connection.commit()
                answer['status'] = "accepted"
                answer['rules'] = result['rules'].decode('utf-8')
        else:
            answer['status'] = "rejected"

        # Commit transaction!
        cursor.execute("COMMIT")
        cursor.close()

        return answer

    # Current function returns a tuple with
    # (notify_email, rules)
    # for a specific job
    def job_get_details(self, job_id):
        assert (isinstance(job_id, int))

        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # or the query returnes more than 1 row
            query = "SELECT description, rules FROM jobs \
                    WHERE `id` = %s LIMIT 1"
            cursor.execute(query, job_id)
            result = cursor.fetchone()

            if result is not None:
                notify_email = None
                # Job still exists!
                job_description = json.loads(result['description'])
                if 'notify_email' in job_description:
                    notify_email = job_description['notify_email']

                # If we want to return more data, we can do it here

                # Return the tuple
                return (notify_email, result['rules'].decode('utf-8'))
            return (None, None)

    # Function used to INSERT into db the list of results it receives
    # TODO: how do I make sure this insert was successful?
    def save_agent_results(self, agent_id, job_results, job_status):
        validators.validate_agent_results(job_results)
        agent_id = str(int(agent_id))
        job_id = str(int(job_results['job_id']))

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        # Let's get the current job description
        cursor.execute("BEGIN")
        self.connection.commit()
        # Let's see if the current job has been assigned meanwhile
        # We use SELECT FOR UPDATE to lock the entire row!
        query = "SELECT * FROM jobs WHERE `id` = %s FOR UPDATE"
        cursor.execute(query, job_id)
        query_result = cursor.fetchone()

        # Now we append to description the execution time
        if query_result is not None:
            # From description and update some values (if needed!)
            # Convert the job description into dict()
            job_description = json.loads(query_result['description'])
            # Add execution time + any errors / warnings reported by yara
            job_description['execution_time'] = job_results['execution_time']
            job_description['yara_errors'] = job_results['yara_errors']
            job_description['yara_warnings'] = job_results['yara_warnings']

            # Insert the hashes into DB!
            # Convert from json to dict
            try:
                md5_hashes = json.loads(job_results['md5_results'])
                # Now that we have a list of md5 hashes, add them to DB
                for md5 in md5_hashes:
                    query = "INSERT IGNORE into jobs_hashes (`job_id`, `hash_md5`) \
                            VALUES (%s, %s)"
                    cursor.execute(query, (job_id, md5))
                    self.connection.commit()

                query = "UPDATE jobs \
                        SET `description` = %s,\
                            `results`= %s, \
                            `matched_files` = %s, \
                            `status` = %s, \
                            `finish_time` = %s \
                        WHERE `id` = %s"
                cursor.execute(query, (
                    json.dumps(job_description, ensure_ascii=True),
                    job_results['yara_results'],
                    job_results['matched_files'],
                    job_status,
                    job_results['finish_time'],
                    job_id)
                )
                self.connection.commit()

            except ValueError:
                # We got an error while extracting the md5s
                logging.error(
                    "Could not parse the JSON with md5s received from worker: " + str(job_results['md5_results']))
            except Exception as e:
                logging.error(
                    'General failure when trying to insert the job in db: %s', e)

        else:
            # If the current job doesn't exist any more, we just pass,
            # losing the results?!
            pass

        # Commit transaction!
        cursor.execute("COMMIT")
        self.connection.commit()


class notification():
    # def __init__(self):

    def email(self, data):
        assert (isinstance(data, dict))

        mail = MIMEText(data['body'])
        mail['From'] = config.notification_email_from
        mail['To'] = data['to']
        mail['Subject'] = data['subject']
        if len(data['to']) > 0 and data['to'] != "no_emails_needed" and config.notification_email_enabled:
            try:
                smtp = smtplib.SMTP(config.notification_email_smtp_srv)
                smtp.sendmail(config.notification_email_from,
                              data['to'],
                              mail.as_string())
                smtp.quit()
                return True
            # We are catching all exceptions, since we are running in daemon
            # mode anyway
            except Exception:
                return False


class validators():

    @classmethod
    def validate_agent_results(cls, entry):
        assert (isinstance(entry, dict))
        assert ('job_id' in entry)
        assert ('finish_time' in entry)
        assert ('fileset_scan' in entry)
        assert ('execution_time' in entry)
        assert ('yara_errors' in entry)
        assert ('yara_warnings' in entry)
        assert ('matched_files' in entry)
        assert ('md5_results' in entry)

        # And finally!
        assert ('yara_results' in entry)
        return
