import { useState, useContext } from 'react';
import MyJobCard from './MyJobCard';
import { ProviderContext } from '../../context/context';

const ProfileDetail = () => {
    const { session } = useContext(ProviderContext);
    const [selectedCvId, setSelectedCvId] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
   
    const handleAnalyse = (cvId) => {
        setSelectedCvId(cvId);
    };

    const data = [
        { id: "8cbd6090-800e-4535-95bd-466d96ce97b8", name: "AI Engineering Role" },
        { id: "d8936b36-eddb-4fb2-aaeb-33b7d7535f42", name: "Data Engineering Role" },
        { id: "8204d7df-5d15-4de6-968e-c49fde996000", name: "ML Engineering Role" },
        { id: "9290280c-fcd5-4360-949f-6d2645df7bb9", name: "Software Engineering Role" }
    ];

    const filteredData = data.filter(item =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className='m-5'>
            <div className='flex justify-between'>
                <div className='relative m-2'>
                    <button className='bg-red-500 w-56 rounded p-2'>
                        CV List
                    </button>
                    <div className='absolute overflow-auto max-h-[35rem] z-10 mt-2 rounded bg-gray-100 py-4 px-5 w-56'>
                        {session !== undefined ? (
                            session.map((item, index) => (
                                <div className='mb-4 hover:bg-white p-2 cursor-pointer rounded' key={index}>
                                    <button onClick={() => handleAnalyse(item.sessionId)}>
                                        {item.fileName}
                                    </button>
                                </div>
                            ))
                        ) : (
                            <div className='p-2 text-gray-500'>No CVs available</div>
                        )}
                    </div>
                </div>

                <div className='flex-grow m-2'>
                    <div className='flex justify-end items-center mb-4'>
                        <input
                            type="text"
                            className='p-2 rounded-full border w-96'
                            placeholder='Search job'
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)} />
                    </div>

                    <div className='flex flex-wrap gap-10 mx-24 mt-3'>
                        {filteredData.map((job) => (
                            <MyJobCard key={job.id} item={job} selectedCvId={selectedCvId} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfileDetail;