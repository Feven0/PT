import '../styles/LoadingSpinner.css'; 

interface Style {
    style: any
}
const LoadingSpinner: React.FC<Style>=({ style }) => {
    return (
        <div className="loading-spinner" style={style}></div>
    );
};

export default LoadingSpinner;