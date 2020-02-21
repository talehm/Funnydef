from subprocess import Popen, PIPE

p = Popen(["curl", "-k", "-X", "POST", "-H", "api-key: 3049de80-5491-11ea-8f72-af685da1b20e", "-H", "Content-Type: application/json",    "http://api.cortical.io/rest/text/keywords?retina_name=en_associative", "-d", "@test.txt"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
output, err = p.communicate(b"input data that is passed to subprocess' stdin")
rc = p.returncode
print(output)