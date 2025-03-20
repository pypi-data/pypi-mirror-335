def text2speech():
    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical"
            android:gravity="center"
            android:padding="20dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="TEXT TO SPEECH APPLICATION"
                android:textSize="20sp"
                android:textStyle="bold"
                android:paddingBottom="20dp"/>

            <EditText
                android:id="@+id/inputText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Enter text here"
                android:padding="10dp"/>

            <Button
                android:id="@+id/speakButton"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Convert Text to Speech"
                android:layout_marginTop="20dp"/>
        </LinearLayout>
        """,
        """
        package com.example.program7tts;

        import android.os.Bundle;
        import android.speech.tts.TextToSpeech;
        import android.view.View;
        import android.widget.Button;
        import android.widget.EditText;
        import androidx.appcompat.app.AppCompatActivity;
        import java.util.Locale;

        public class MainActivity extends AppCompatActivity {

            private EditText inputText;
            private Button speakButton;
            private TextToSpeech textToSpeech;

            @Override
            protected void onCreate(Bundle savedInstanceState) {
            
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                inputText = findViewById(R.id.inputText);
                speakButton = findViewById(R.id.speakButton);

                // Initialize TextToSpeech
                textToSpeech = new TextToSpeech(getApplicationContext(), status -> {
                    if (status != TextToSpeech.ERROR) {
                        textToSpeech.setLanguage(Locale.US);
                    }
                });

                // Set click listener for the button
                speakButton.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        String text = inputText.getText().toString();
                        if (!text.isEmpty()) {
                            textToSpeech.speak(text, TextToSpeech.QUEUE_FLUSH, null, null);
                        }
                    }
                });
            }

            @Override
            protected void onDestroy() {
                if (textToSpeech != null) {
                    textToSpeech.stop();
                    textToSpeech.shutdown();
                }
                super.onDestroy();
            }
        }
        """
    ]