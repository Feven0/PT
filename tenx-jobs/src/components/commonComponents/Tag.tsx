import { Tag } from 'antd';
import { forwardRef } from "react";

export type TagProps = {
    text: string;
    type: "high1" | "high2" | "high3" | "mid4" | "mid5" | "mid6" | "low7" | "low8" | "low9" | "neutral10" | "info11";
};

const TagComponent = forwardRef<HTMLSpanElement, TagProps>(({ type, text }, ref) => {
    
    switch (type) {
        // tag1: Completed
        case "neutral10":
            return (
                <Tag ref={ref} color="#F5F5F5" style={{ color: "#000000A6", border: "1px solid #D9D9D9", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
        // tag2: Not Started
        case "low9":
            return (
                <Tag ref={ref} color="#FFFBE6" style={{ color: "#874D00", border: "1px solid #FFE58F", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
        // tag3: Draft
        case "mid4":
            return (
                <Tag ref={ref} color="#E6F4FF" style={{ color: "#1677FF", border: "1px solid #91CAFF", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
        // Not Completed
        case "info11":
            return (
                <Tag ref={ref} color="#FFF0F6" style={{ color: "#EB2F96", border: "1px solid #FFADD2", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
        case "high1":
            return (
                <Tag ref={ref} color="#F6FFED" style={{ color: "#52C41A", border: "1px solid #B7EB8F", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
        case "high2":
            return (
                <Tag ref={ref} color="#E9FFE9" style={{ color: "#00E200", border: "1px solid #7AFF7A", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
        case "high3":
            return (
                <Tag ref={ref} color="#FCFFE6" style={{ color: "#A0D911", border: "1px solid #EAFF8F", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
        case "mid5":
            return (
                <Tag ref={ref} color="#DCF4F4" style={{ color: "#008080", border: "1px solid #64C9C9", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
        case "mid6":
            return (
                <Tag ref={ref} color="#E6FFFB" style={{ color: "#13C2C2", border: "1px solid #87E8DE", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
        case "low7":
            return (
                <Tag ref={ref} color="#FFF7E6" style={{ color: "#FA8C16", border: "1px solid #FFD591", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
        case "low8":
            return (
                <Tag ref={ref} color="#FFF7E6" style={{ color: "#D48806", border: "1px solid #FFD666", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );

        default:
            return (
                <Tag ref={ref} color="#F6FFED" style={{ color: "#000000", border: "1px solid #000000", marginBottom:"0.5rem" }}>
                    {text}
                </Tag>
            );
    }
}
);

export default TagComponent;