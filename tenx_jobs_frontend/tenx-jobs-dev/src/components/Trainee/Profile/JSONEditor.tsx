import {useEffect, useRef, useState } from "react";
import { Flex, Typography } from "antd";
import { CheckOutlined, CloseCircleOutlined } from "@ant-design/icons";
import Editor from "@monaco-editor/react";
import Ajv from "ajv"

import { setProfileJson } from "../../../redux/slices/profileUploadSlice";
import { resumeSchema } from "../../../types/jsonProfileTypes";
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";

const { Text } = Typography;

export default function JSONEditor() {
  const editorRef = useRef(null);
  const dispatch = useAppDispatch();
  const [validate, setValidate] = useState<boolean>(false);
  const {profileJson} = useAppSelector(state => state.profileUpload);
  const {profile, type, profileErrorText} = profileJson;
  const profileJsonString = profile ? profile : "";

  const ajv = new Ajv()
  const profileIsValid = (rub: any) => {
    const validate = ajv.compile(resumeSchema)
    const valid = validate(rub)
    if (!valid) {
        console.log(validate.errors)
    }
    return valid
  }

  

  const isJsonString = (str: string) => {
    try {
        const json = JSON.parse(str);
        if (json && typeof json === "object") {
            return json;
        }
    } catch (e) {
        return false;
    }
    return false;
  }
  


  useEffect(() => {
    if (isJsonString(JSON.stringify(profile, null, 2)) && profileIsValid(JSON.parse(profile))) {
        dispatch(setProfileJson({ ...profileJson, profileErrorText: "" }))
    } else {
        dispatch(setProfileJson({ ...profileJson, profileErrorText: "Invalid JSON!" }))
    }
  }, [profile])

  useEffect(() => {
    if (type === 'profile') {
        dispatch(setProfileJson({ 
            ...profileJson, 
            profileErrorText: ""
        }))
    }
  }, [type])
   
  const handleInputChange = (value: string | undefined) => {
    if (value !== undefined) {
      try {
        JSON.parse(value);
        dispatch(setProfileJson({
            ...profileJson,
            profile: value,
            profileErrorText: ""
        }))
        setValidate(false); 
      } catch (error) {
        dispatch(setProfileJson({
            ...profileJson,
            profileErrorText: "Invalid JSON!"
        }))
        setValidate(true);
      }
    }
  };

    const onMount = (editor:any) => {
        editorRef.current = editor;
        editor.focus();
      }

  return (
    <Flex vertical style={{gap:"0.5rem", border:"1px solid #D9D9D9", borderRadius:"0.25rem"}}>
        <Editor
            height="40vh"
            width={"100%"}
            language="json"
            theme="vs-light"
            onMount={onMount}
            value={profileJsonString}
            onChange={handleInputChange}
            options={{
                minimap: { enabled: true },
                scrollBeyondLastLine: false,
                wordWrap: "on",
                wrappingIndent: "indent",
                wrappingStrategy: "advanced",
                padding: { top: 10, bottom: 10 },
              }}
              className={validate ? "json-content-editor-error" : ""}
          />
           <Text style={{ color: validate ? '#FAAD14' : 'green' }}>
             {validate ? <>{profileErrorText} <CloseCircleOutlined /></> : <div className="d-flex gap-8">Valid JSON <CheckOutlined /></div>}
        </Text>
    </Flex>
  )
}