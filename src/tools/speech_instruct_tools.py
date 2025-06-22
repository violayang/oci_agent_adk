# Convert Speech to Text
import oci

def getSigner(profile_name):
    config = oci.config.from_file(profile_name=profile_name)
    signer = oci.signer.Signer(
        tenancy=config['tenancy'],
        user=config['user'],
        fingerprint=config['fingerprint'],
        private_key_file_location=config['key_file'],
        pass_phrase=config.get('pass_phrase')
    )
    return config, signer

def getSpeechClient():
    config, signer = getSigner("DEFAULT") # Change the profile name from DEFAULT, if you are using some other profile
    ai_client = oci.ai_speech.AIServiceSpeechClient(config, signer=signer)
    return ai_client

ai_client = getSpeechClient()

# Give your job related details in these fields
SAMPLE_DISPLAY_NAME = "<job_name>"
SAMPLE_COMPARTMENT_ID = "<compartment_id>"
SAMPLE_DESCRIPTION = "<job_description>"
SAMPLE_NAMESPACE = "<sample_namespace>"
SAMPLE_BUCKET = "<bucket_name>"
JOB_PREFIX = "Python_SDK_DEMO"
LANGUAGE_CODE = "en-US"
FILE_NAMES = ["<file1>", "<file2>"]
NEW_COMPARTMENT_ID = "<new_compartment>"
NEW_DISPLAY_NAME = "<new_name>"
NEW_DESCRIPTION = "<new_description>"
MODEL_TYPE = "WHISPER_MEDIUM"

SAMPLE_MODEL_DETAILS = oci.ai_speech.models.TranscriptionModelDetails(model_type=MODEL_TYPE, domain="GENERIC",  language_code=LANGUAGE_CODE,
transcription_settings=oci.ai_speech.models.TranscriptionSettings(
    diarization=oci.ai_speech.models.Diarization(
        is_diarization_enabled=True    # Boolean value to enable or disable diarization
    )
)
)
SAMPLE_OBJECT_LOCATION = oci.ai_speech.models.ObjectLocation(namespace_name=SAMPLE_NAMESPACE, bucket_name=SAMPLE_BUCKET,
object_names=FILE_NAMES)
SAMPLE_INPUT_LOCATION = oci.ai_speech.models.ObjectListInlineInputLocation(
    location_type="OBJECT_LIST_INLINE_INPUT_LOCATION", object_locations=[SAMPLE_OBJECT_LOCATION])
SAMPLE_OUTPUT_LOCATION = oci.ai_speech.models.OutputLocation(namespace_name=SAMPLE_NAMESPACE, bucket_name=SAMPLE_BUCKET,
                                                             prefix=JOB_PREFIX)
COMPARTMENT_DETAILS = oci.ai_speech.models.ChangeTranscriptionJobCompartmentDetails(compartment_id=NEW_COMPARTMENT_ID)
UPDATE_JOB_DETAILS = oci.ai_speech.models.UpdateTranscriptionJobDetails(display_name=NEW_DISPLAY_NAME, description=NEW_DESCRIPTION)

# Create Transcription Job with details provided
transcription_job_details = oci.ai_speech.models.CreateTranscriptionJobDetails(display_name=SAMPLE_DISPLAY_NAME,
                                                                               compartment_id=SAMPLE_COMPARTMENT_ID,
                                                                               description=SAMPLE_DESCRIPTION,
                                                                               model_details=SAMPLE_MODEL_DETAILS,
                                                                               input_location=SAMPLE_INPUT_LOCATION,
                                                                               output_location=SAMPLE_OUTPUT_LOCATION)

transcription_job = None
print("***CREATING TRANSCRIPTION JOB***")
try:
    transcription_job = ai_client.create_transcription_job(create_transcription_job_details=transcription_job_details)
except Exception as e:
    print(e)
else:
    print(transcription_job.data)