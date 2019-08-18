import re
import csv
import yaml
import praw

def process_username(username):
    """Return a link to a user's profile."""
    username = re.sub(r"(?i)/?(u/)?|\s.+", "", username)
    return f"https://www.reddit.com/user/{username}"

def process_answer(answer):
    """Return the answer in a Reddit markdown code block."""
    answer = [f"    {line}" for line in answer.split("\n")]
    return "\n".join(answer)

def main():
    """Do the things"""
    # read config from file
    with open("config.yml", "r") as config_file:
        config = yaml.safe_load(config_file)

    # Read user data from file
    with open("data.csv", newline="") as data_file:
        reader = csv.reader(data_file)
        responses = list(reader)

    # the questions are just the first row of the data
    questions = responses.pop(0)

    print(f"processing {len(responses)} responses")

    # generate all the comments we need to make
    comment_bodies = []
    for response_answers in responses:
        # generate a comment body for this response
        comment_body = ""
        for index, answer in enumerate(response_answers):
            # we include the question with every answer
            question = questions[index]
            if question in config["ignored_questions"]:
                # don't show ignored questions
                continue
            elif question == config["username_question"]:
                # username is special-cased so we can generate a profile link
                answer = process_username(answer)
            else:
                # other answers just get shoved in a code block
                answer = process_answer(answer)
            # add this answer to the comment body
            comment_body += f"### {question}\n\n{answer}\n\n"
        # add this comment to the list to be added
        comment_bodies.append(comment_body)

    # create reddit instance
    r = praw.Reddit(**config["reddit"])

    # get the submission we're gonna be adding comments on
    submission = r.submission(id=config["target_submission_id"])

    # make the comments all at once
    failed_users = []
    for index, comment_body in enumerate(comment_bodies):
        print(index)
        try:
            submission.reply(comment_body).clear_vote()
        except praw.exceptions.APIException as e:
            print(e)
            failed_users.append(comment_body)

    with open("failed.txt", "w+") as file:
        for comment in failed_users:
            file.write(comment)
            file.write("=====\n\n")

    print("done woo")

if __name__ == "__main__":
    main()
