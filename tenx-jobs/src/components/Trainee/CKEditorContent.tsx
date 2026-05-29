import parse, { HTMLReactParserOptions } from 'html-react-parser';

// Styles
import '../../styles/slidingCard.css'

type DataProps = {
    content: string;
};

export default function CKEditorContent({ content }: DataProps) {
    const options: HTMLReactParserOptions = {
        replace: (node: any) => {
            if (node.type === 'tag' && node.name === 'oembed') {
                const url = node.attribs.url;
                if (url.includes('youtube')) {
                    const videoId = url.split('v=')[1];
                    return (
                        <iframe
                            title="YouTube Video"
                            className="video-item"
                            height="315"
                            src={`https://www.youtube.com/embed/${videoId}`}
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowFullScreen
                        ></iframe>
                    );
                } else if (url.includes('vimeo')) {
                    const videoId = url.split('/')[3];
                    return (
                        <iframe
                            title="Vimeo Video"
                            src={`https://player.vimeo.com/video/${videoId}`}
                            className="video-item"
                            height="360"
                            allow="autoplay; fullscreen; picture-in-picture"
                            allowFullScreen
                        ></iframe>
                    );
                } else if (url.includes('dailymotion')) {
                    const videoId = url.split('/')[4].split('?')[0];
                    return (
                        <iframe
                            title="Daily motion Video"
                            className="video-item"
                            height="270"
                            src={`https://www.dailymotion.com/embed/video/${videoId}`}
                            allow="autoplay"
                            allowFullScreen
                        ></iframe>
                    );
                } else if (url.includes('drive.google.com')) {
                    const videoId = url.split('/')[5];
                    return (
                        <iframe
                            title="Google Drive Video"
                            className="video-item"
                            height="360"
                            src={`https://drive.google.com/file/d/${videoId}/preview`}
                            allow="autoplay; fullscreen"
                            allowFullScreen
                        ></iframe>
                    );
                }
            } else if (node.type === 'tag' && node.name === 'figure') {
                const children = node.children;
                let oembedUrl = '';
                for (let i = 0; i < children.length; i++) {
                    if (children[i].type === 'tag' && children[i].name === 'oembed') {
                        oembedUrl = children[i].attribs.url;
                    }
                }
                if (oembedUrl.includes('instagram')) {
                    return (
                        <blockquote className="instagram-media">
                            <a href={oembedUrl}></a>
                        </blockquote>
                    );
                } else if (oembedUrl.includes('twitter')) {
                    return (
                        <blockquote className="twitter-tweet">
                            <a href={oembedUrl}></a>
                        </blockquote>
                    );
                }
            }
        },
    };

    return (
        <div className="ck-content trainee-job-details-content">
            {parse(content, options)}
        </div>
    );
}
