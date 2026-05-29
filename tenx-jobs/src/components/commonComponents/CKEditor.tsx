import { CKEditor } from '@ckeditor/ckeditor5-react';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';

export default function CkEditor({ value, onDataChange }: { value: string, onDataChange: (value: string) => void }) {
  return (
    <div>
      <CKEditor
        editor={ClassicEditor as any}
        config={{
          toolbar: {
            items: [
                'undo', 'redo',
                '|', 'heading',
                '|', 'bold', 'italic',
                '|', 'link', 'blockQuote', 'mediaEmbed',
                '|', 'insertTable', 'tableColumn', 'tableRow', 'mergeTableCells',
                '|', 'bulletedList', 'numberedList', 'outdent', 'indent'
                
            ],
            shouldNotGroupWhenFull: false
        },

        }}
        
        data={value}
        onChange={(_event, editor: any) => {
          const text = editor.getData();
          onDataChange(text);
        }}
      />
    </div>
  )
}
