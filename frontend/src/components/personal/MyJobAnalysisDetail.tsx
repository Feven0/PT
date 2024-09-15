import {useState} from 'react'

const MyJobAnalysisDetail = ({analysis}) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const totalSlides = Math.ceil(analysis?.analysis?.section.length / 2) + 1;

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1 < totalSlides ? prev + 1 : prev));
  };

  const prevSlide = () => {
      setCurrentSlide((prev) => (prev - 1 >= 0 ? prev - 1 : prev));
  };

  const getSlideContent = (index) => {
    const start = index * 2;
    const end = start + 2;
    const sectionsToShow = analysis?.analysis?.section.slice(start, end);

    return sectionsToShow.map((item, idx) => (
      <div key={idx} className="mb-4">
        <h2 className="text-xl font-semibold text-[red]">{item.title}</h2>
        <p className="text-gray-700">{item.description}</p>
      </div>
    ));
  };

  
  return (
    <div className='chat_scroll p-4 w-96 overflow-auto border shadow-xl py-16 rounded-lg'
    style={{ width: '120vh' }} >
      
      <h1 className="text-2xl font-bold text-center mb-4">{analysis?.analysis?.header}</h1>
      <div className="relative my-16">
        <div className="slider mb-10">
            {Array.from({ length: totalSlides - 1 }).map((_, index) => (
                <div 
                    key={index} 
                    className={`slide ${currentSlide === index ? 'active' : 'hidden'}`}
                >
                    {getSlideContent(index)}
                </div>
            ))}
            <div className={`slide ${currentSlide === totalSlides - 1 ? 'active' : 'hidden'}`}>
                <h2 className="text-xl font-semibold text-[red]">Overall Analysis</h2>
                <p className="text-gray-700">{analysis?.analysis?.overall}</p>
            </div>
        </div>

        <div className="">
            {currentSlide > 0 && (
                <button onClick={prevSlide} className="absolute left-0 transform -translate-y-1/2 w-32 bg-gray-500 text-white p-1 rounded-lg">
                    Previous
                </button>
            )}
            {currentSlide < totalSlides - 1 && (
                <button onClick={nextSlide} className="absolute right-0 transform -translate-y-1/2 w-32 bg-gray-500 text-white p-1 rounded-lg">
                    Next
                </button>
            )}
        </div>
      </div>

    </div>
  )
}

export default MyJobAnalysisDetail