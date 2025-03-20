CREATE OR REPLACE FUNCTION schema_inference(data string, name string, description string, type string, ids string, properties string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
import json
from neutrino.onboard.agent import DataOnboardingAgent


def schema_inference(data, name, description, type, ids, properties):
    results = []
    for (data, name, description, type, ids, properties) in zip(data, name, description, type, ids, properties):
        try:
            agent = DataOnboardingAgent()
            result = {}
            if type == "append_only":
                inference_ddl, inference_json = agent.inference(data, name, description)
                result["ddl"] = inference_ddl
                result["json"] = inference_json
            elif type == "mutable_stream":
                inference_ddl, inference_json = agent.inference_mutable_stream(data, name, ids, description)
                result["ddl"] = inference_ddl
                result["json"] = inference_json
            elif type == "external":
                inference_ddl, inference_json = agent.inference_external_stream(data, name, properties, description)
                result["ddl"] = inference_ddl
                result["json"] = inference_json
            
            results.append(json.dumps(result))
            
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;


CREATE OR REPLACE FUNCTION field_summary(data string, ddl string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
from neutrino.onboard.agent import DataOnboardingAgent


def field_summary(data, ddl):
    results = []
    for (data, ddl) in zip(data, ddl):
        try:
            agent = DataOnboardingAgent()
            summary_result = agent.summary(data, ddl)
            results.append(summary_result)
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;

CREATE OR REPLACE FUNCTION analysis_recommendation(data string, ddl string, name string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
from neutrino.onboard.agent import DataOnboardingAgent


def analysis_recommendation(data, ddl, name):
    results = []
    for (data, ddl, name) in zip(data, ddl, name):
        try:
            agent = DataOnboardingAgent()
            recommendation_result = agent.recommendations(data, ddl, name)
            results.append(recommendation_result)
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;