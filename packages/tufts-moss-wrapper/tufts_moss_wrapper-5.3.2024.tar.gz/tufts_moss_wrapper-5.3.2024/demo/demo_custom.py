def simplify_folder(submission_path):
    return submission_path.lstrip("demo/")

def remove_fake(submission_filepath):
    return "fakestudent" not in submission_filepath