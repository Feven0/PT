import { Link } from "react-router-dom"

const MyJobCard = ({item, selectedCvId}) => {

    return (
        <>
            <div className='bg-white border border-opacity-10 h-44 w-80 shadow-xl rounded-lg font-roboto'>
                <div className='p-2 py-4'>
                    <h1 className='text-xl text-center'>{item.name}</h1>
                </div>
                <div className=''>
                    {/* <h1 className='text-xl text-center'>{item.description}</h1> */}
                    <h1 className='text-gray-400 mx-2'>Lorem ipsum dolor, sit amet consectetur adipisicing elit. ....</h1>
                </div>
                <div className='flex justify-between mx-3 bottom-0'>
                    <p 
                    className='border border-red-200 cursor-pointer shadow-xl rounded mt-3 p-1 px-3'
                    >
                        Match?
                    </p>
                    <Link to={`/main_activity/${item.id}/${selectedCvId}`}>
                        <button className='text-red-600 mt-6'>
                            continue
                        </button>
                    </Link>
                </div>
            </div>
        </>
    )
}

export default MyJobCard